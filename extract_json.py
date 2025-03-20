from bs4 import BeautifulSoup
import os
import json

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



cardlist_path = 'Cardlists'     #path to directory with all the html files containing card data
for filename in os.listdir(cardlist_path):      #iterates over every file in the directory
    with open(os.path.join(cardlist_path, filename), 'r') as f:
        #parses html file using BeautifulSoup
        soup = BeautifulSoup(f, 'html.parser', multi_valued_attributes=None)
        #finds the name of the selected filter from html
        selection = soup.find('option', selected=True)
        print(selection.text)
        #finds all the card blocks within the html
        dl_list = soup.find_all('dl', class_='modalCol')
        #splits the card block into infoCol, cardName, frontCol, and backCol
        for dl in dl_list:
            infoCols = dl.find_all('div', class_='infoCol')
            cardNames = dl.find_all('div', class_='cardName')
            frontCols = dl.find_all('div', class_='frontCol')
            backCols = dl.find_all('div', class_='backCol')
            for infoCol, cardName, frontCol, backCol in zip(infoCols, cardNames, frontCols, backCols):
                #extracts card id, rarity, and type
                info = infoCol.text.split('|')
                card_id = info[0].strip()
                rarity = info[1].strip()
                card_type = info[2].strip()
                info = [x.strip() for x in info]
                #print(info)
                name = cardName.text
                #removes Cost prefix for characters, events, and stages, as well as removes Life prefix for Leaders
                cost = backCol.find('div', class_='cost').text.removeprefix('Cost').removeprefix('Life')
                #removes everything except the actual attribute itself
                attribute = backCol.find('div', class_='attribute').text.removeprefix('\nAttribute\n').removesuffix('\n')
                #removes Power prefix and leaves only the power value itself
                power = backCol.find('div', class_='power').text.removeprefix('Power')
                #removes Counter prefix and leaves only the counter value itself
                counter = backCol.find('div', class_='counter').text.removeprefix('Counter').removesuffix('-')
                #removes Color prefix and leaves only the color itself
                color = backCol.find('div', class_='color').text.removeprefix('Color')
                #removes Type prefix and leaves just the type itself
                feature = backCol.find('div', class_='feature').text.removeprefix('Type')
                #removes Effect prefix leaving only the effects themselves
                text = backCol.find('div', class_='text').text.removeprefix('Effect')
                #
                trigger = backCol.find('div', class_='trigger')
                trigger = trigger.text.removeprefix('Trigger') if trigger else ''
                #
                card_set = backCol.find('div', class_='getInfo').text.removeprefix('Card Set(s)-')
                #print(card_set)
                #print(name)
                #print([cost, attribute, power, counter, color, feature, text, trigger])
                #print()
                match card_type:
                    case 'LEADER':
                        card = Leader(card_id, rarity, card_type, card_set, name, cost, attribute, power, counter, color, feature, text, trigger)
                    case 'CHARACTER':
                        card = Character(card_id, rarity, card_type, card_set, name, cost, attribute, power, counter, color, feature, text, trigger)
                    case 'EVENT':
                        card = Event(card_id, rarity, card_type, card_set, name, cost, attribute, power, counter, color, feature, text, trigger)

                print(json.dumps(card.__dict__, indent=4))
                break
            break
        #print(infoCols)


