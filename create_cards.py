import json
import sqlite3
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv
import re
import ast

def get_card_info(cursor, card_id):
    cursor.execute(f"SELECT feature_name FROM feature_cards WHERE card_id='{card_id}'")
    card_features = [x[0] for x in cursor.fetchall()]
    cursor.execute(f"SELECT color_name FROM color_cards WHERE card_id='{card_id}'")
    card_colors = [x[0] for x in cursor.fetchall()]
    cursor.execute(f"SELECT attribute_name FROM attribute_cards WHERE card_id='{card_id}'")
    card_attributes = [x[0] for x in cursor.fetchall()]
    return card_features, card_colors, card_attributes

def get_cards_of_type(card_type, cursor):
    cursor.execute(f"SELECT * FROM cards WHERE card_type='{card_type}'")
    cards = cursor.fetchall()
    relevant_cards = dict()
    for base_card in cards:
        card_dict = dict()
        card_dict['card_id'] = base_card[0]
        card_dict['rarity'] = base_card[1]
        card_dict['card_type'] = base_card[2]
        card_dict['card_set'] = base_card[3]
        card_dict['name'] = base_card[4]
        if card_type == 'LEADER' or card_type == 'CHARACTER':
            card_dict['power'] = base_card[5]
        card_dict['text'] = base_card[7]
        if card_type == 'LEADER':
            card_dict['life'] = base_card[8]
        if card_type != 'LEADER':
            card_dict['cost'] = base_card[9]
            card_dict['trigger'] = base_card[10]
        if card_type == 'CHARACTER':
            card_dict['counter'] = base_card[6]
        card_features, card_colors, card_attributes = get_card_info(cursor, card_dict['card_id'])
        card_dict['feature'] = card_features
        card_dict['color'] = card_colors
        card_dict['attribute'] = card_attributes
        # print(card_dict)
        relevant_cards[card_dict['card_id']] = card_dict
    return dict(sorted(relevant_cards.items()))

def generate_generic_card(card_type, cursor):
    relevant_cards = get_cards_of_type(card_type, cursor)
    card_examples = json.dumps(relevant_cards, indent=4)
    prompt = f"Create a new {card_type} Card for the One Piece Trading Card Game. Use the examples provided as inspiration, but make sure to keep the card original. Format the output like the examples. Examples: {card_examples}"
    response = llm.invoke(prompt)
    return response

def generate_card(card_type, relevant_cards, card_template):
    card_examples = json.dumps(relevant_cards, indent=4)
    prompt = f"Fill in the missing details for the following {card_type} Card for the One Piece Trading Card Game. Card template: {card_template}. Make sure to fill in the missing attributes. Use the examples provided as inspiration, but make sure to keep the card original. Format the output like the examples. Examples: {card_examples}"
    response = llm.invoke(prompt)
    return response

def generate_card_ragchain(card_type, card_template, randomness):
    gen_card_chain = (
            {"card_type": RunnablePassthrough() | (lambda x: card_type),
             "card_examples": vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 10, "fetch_k": 40, "lambda_mult": randomness, "filter": {"card_type": card_type}}) | format_cards,
             "card_template": RunnablePassthrough()}
            | card_prompt
            | llm
            | format_new_card
    )
    card = gen_card_chain.invoke(card_template)
    return card

def format_cards(cards):
    card_examples = ""
    for card in cards:
        card_examples += f"{card.page_content}\n"
    print(f"Cards being used as examples: \n{card_examples}")
    return card_examples

def format_new_card(card):
    cleaned = re.sub(r"^```json|```$", "", card.strip()).strip()
    res = ast.literal_eval(cleaned)
    return json.dumps(res, indent=4)

def get_card_details(card_type):
    print('Enter optional card details:')
    card_template = dict()
    card_template['card_id'] = ''
    if card_type == 'LEADER':
        card_template['rarity'] = 'L'
    card_template['card_type'] = card_type
    card_template['card_set'] = ''
    card_template['name'] = input('Name: ')
    if card_type == "LEADER" or card_type == "CHARACTER":
        card_template['power'] = input('Power: ')
    else:
        card_template['power'] = ''
    if card_type == 'CHARACTER':
        card_template['counter'] = input('Counter: ')
    else:
        card_template['counter'] = ''
    if card_type == 'LEADER':
        card_template['life'] = input('Life: ')
    else:
        card_template['cost'] = input('Cost: ')
    if card_type != "LEADER":
        card_template['color'] = input('Color (Red, Green, Blue, Purple, Black, Yellow): ')
    card_template['text'] = input(f'{card_type.lower().capitalize()}\'s effect: ')
    if card_type != "LEADER":
        card_template['trigger'] = input('Trigger: ')
    print('For the next features if you wish to specify multiple separate them with commas')
    card_template['feature'] = input('Features (ex. Straw Hat Crew, Fishman): ').split(',')
    if card_type == "LEADER":
        card_template['color'] = input('Colors (Red, Green, Blue, Purple, Black, Yellow): ').split(',')
    if card_type == "LEADER" or card_type == "CHARACTER":
        card_template['attribute'] = input('Attributes: (Slash, Ranged, Special, Strike, Wisdom): ').split(',')
    else:
        card_template['attribute'] = ''
    if card_type == "LEADER":
        card_template['trigger'] = ''
    print("How random do you want the missing details to be? 0(random) - 1(similar to cards sharing same details)")
    try:
        lambda_mult = float(input('Enter a decimal between 0 and 1: '))
    except ValueError:
        print("Invalid input. Please enter a valid decimal number next time. randomness set to default of 0.8")
        lambda_mult = 0.8
    print("Card generated using RAG chain:")
    result = generate_card_ragchain(card_type, str(card_template), lambda_mult)
    return result

def ask_user(card_type, cursor):
    while True:
        print('Would you like to specify card details?')
        print('1. Yes')
        print('2. No, generate a completely random card')
        choice = input('Enter your choice (1-2): ')
        if choice == '2':
            card = generate_generic_card(card_type, cursor)
            return card
        elif choice == '1':
            card = get_card_details(card_type)
            return card
        else:
            print('Invalid choice. Please try again.')
            continue
    return None

def create_card(card_database):
    sqlite_connection = sqlite3.connect(card_database)
    cursor = sqlite_connection.cursor()
    while True:
        print('What card type would you like to create?')
        print('1. Leader')
        print('2. Character')
        print('3. Event')
        print('4. Stage')
        print('5. Exit')
        choice = input('Enter your choice (1-5): ')
        if choice == '1':
            card_type = 'LEADER'
            card = ask_user(card_type, cursor)
            print("Here is your generated card:")
            print(card)

        elif choice == '2':
            card_type = 'CHARACTER'
            card = ask_user(card_type, cursor)
            print("Here is your generated card:")
            print(card)

        elif choice == '3':
            card_type = 'EVENT'
            card = ask_user(card_type, cursor)
            print("Here is your generated card:")
            print(card)

        elif choice == '4':
            card_type = 'STAGE'
            card = ask_user(card_type, cursor)
            print("Here is your generated card:")
            print(card)

        elif choice == '5':
            break
        else:
            print('Invalid choice. Please try again.')
            continue

load_dotenv()
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv("GOOGLE_API_KEY"))
llm = GoogleGenerativeAI(model="gemini-2.0-flash")

vector_store = Chroma(
    collection_name="OPTCGCards",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db_texts",
)

card_prompt = PromptTemplate.from_template("Fill in the missing details for the following {card_type} Card for the One Piece Trading Card Game. Card template: {card_template}. Make sure to fill in the missing attributes. Use the examples provided as inspiration, but make sure to keep the card original. Format the output like the examples. Examples: {card_examples}")
create_card('asia-cards.db')

