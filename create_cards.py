import json
import sqlite3
from google import genai
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv
load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv("GOOGLE_API_KEY"))

class Card:
    def __init__(self, card_id, rarity, card_type, card_set, name, attribute, power, counter, color, feature, text, trigger):
        self.card_id = card_id
        self.rarity = rarity
        self.card_type = card_type
        self.card_set = card_set
        self.name = name
        self.attribute = attribute
        self.power = power
        self.counter = counter
        self.color = color
        self.feature = feature
        self.text = text
        self.trigger = trigger

class Leader(Card):
    def __init__(self, card_id, rarity, card_type, card_set, name, life, attribute, power, counter, color, feature, text, trigger):
        super().__init__(card_id, rarity, card_type, card_set, name, attribute, power, counter, color, feature, text, trigger)
        self.life = life

class Character(Card):
    def __init__(self, card_id, rarity, card_type, card_set, name, cost, attribute, power, counter, color, feature, text, trigger):
        super().__init__(card_id, rarity, card_type, card_set, name, attribute, power, counter, color, feature, text, trigger)
        self.cost = cost

class Event(Card):
    def __init__(self, card_id, rarity, card_type, card_set, name, cost, attribute, power, counter, color, feature, text, trigger):
        super().__init__(card_id, rarity, card_type, card_set, name, attribute, power, counter, color, feature, text, trigger)
        self.cost = cost

class Stage(Card):
    def __init__(self, card_id, rarity, card_type, card_set, name, cost, attribute, power, counter, color, feature, text, trigger):
        super().__init__(card_id, rarity, card_type, card_set, name, attribute, power, counter, color, feature, text, trigger)
        self.cost = cost

def get_card_info(cursor, card_id):
    #sqlite_connection = sqlite3.connect(card_database)
    #cursor = sqlite_connection.cursor()
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
    card_context = json.dumps(relevant_cards, indent=4)
    response =  client.models.generate_content(
        model="gemini-2.0-flash", contents=[
            f"Create a new {card_type} Card for the One Piece Trading Card Game. Use the examples provided as inspiration, but make sure to keep the card original. Format the result in the same json format as the examples. Examples: {card_context}"]
    )
    return response

def generate_card(card_type, cursor, relevant_cards, card_template):
    card_context = json.dumps(relevant_cards, indent=4)
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=[
            f"Fill in the missing details for the following {card_type} Card for the One Piece Trading Card Game. Card template: {card_template}. Make sure to use the values in the card template and fill in missing attributes. Use the examples provided as inspiration, but make sure to keep the card original. Examples: {card_context}"]
    )
    return response

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
            while True:
                print('Would you like to specify card details?')
                print('1. Yes')
                print('2. No, generate a completely random card')
                choice = input('Enter your choice (1-2): ')
                if choice == '2':
                    card = generate_generic_card(card_type, cursor)
                    print(card.text)
                    break
                elif choice == '1':
                    print('Enter optional card details:')
                    card_template = dict()
                    card_template['name'] = input('Name: ')
                    card_template['power'] = input('Power: ')
                    card_template['life'] = input('Life: ')
                    card_template['text'] = input('Leader\'s effect: ')
                    print('For the next features if you wish to specify multiple separate them with commas')
                    card_template['feature'] = input('Features (ex. Straw Hat Crew, Fishman): ').split(',')
                    card_template['color'] = input('Colors (Red, Green, Blue, Purple, Black, Yellow): ').split(',')
                    card_template['attribute'] = input('Attributes: (Slash, Ranged, Special, Strike, Wisdom): ').split(',')
                    #set attributes user should not set as blank
                    card_template['card_id'] = ''
                    card_template['card_set'] = ''
                    card_template['counter'] = ''
                    card_template['trigger'] = ''
                    #ground card type
                    card_template['card_type'] = card_type
                    card_template['rarity'] = 'L'
                    similar_leaders = vector_store.similarity_search(query=str(card_template), k=5, filter={"card_type": card_type})
                    relevant_cards = ""
                    for lead in similar_leaders:
                        print(f"* {lead.page_content} [{lead.metadata}]")
                        relevant_cards += lead.page_content + ",\n"
                    card = generate_card(card_type, cursor, relevant_cards, str(card_template))
                    print(card.text)
                    break
                else:
                    print('Invalid choice. Please try again.')
                    continue

        elif choice == '2':
            card_type = 'CHARACTER'
            print('Would you like to specify card details?')
            print('1. Yes')
            print('2. No, generate a completely random card')
            choice = input('Enter your choice (1-2): ')
            if choice == 2:
                card = generate_generic_card(card_type, cursor)
                print(card.text)
                break
            elif choice == 1:
                print('Enter optional card details:')
                break
            else:
                print('Invalid choice. Please try again.')
                continue

        elif choice == '3':
            card_type = 'EVENT'
            print('Would you like to specify card details?')
            print('1. Yes')
            print('2. No, generate a completely random card')
            choice = input('Enter your choice (1-2): ')
            if choice == 2:
                card = generate_generic_card(card_type, cursor)
                print(card.text)
                break
            elif choice == 1:
                print('Enter optional card details:')
                break
            else:
                print('Invalid choice. Please try again.')
                continue

        elif choice == '4':
            card_type = 'STAGE'
            print('Would you like to specify card details?')
            print('1. Yes')
            print('2. No, generate a completely random card')
            choice = input('Enter your choice (1-2): ')
            if choice == 2:
                card = generate_generic_card(card_type, cursor)
                print(card.text)
                break
            elif choice == 1:
                print('Enter optional card details:')
                break
            else:
                print('Invalid choice. Please try again.')
                continue
        elif choice == '5':
            break
        else:
            print('Invalid choice. Please try again.')
            continue

vector_store = Chroma(
    collection_name="OPTCG",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db",
)
leader = str(Leader('','L','LEADER', '','', '',[''],'','',['Red'],['Strawhat'],'','').__dict__)
results = vector_store.similarity_search(query=leader,k=5)
for doc in results:
    print(f"* {doc.page_content} [{doc.metadata}]")
create_card('asia-cards.db')