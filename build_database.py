import sqlite3
import json

# Builds sq_lite database and fills it using a given cardlist .json and database name.
# Running build_database.py automatically uses the asia-cardlist and creates a database
# named 'asia-cards.db'

# If database/data exists, it will update the tables rather than completely remake them.
def build_sqlite(json_name, database_name):
    try:
        # Create database and/or connect to database
        sqlite_connection = sqlite3.connect(database_name)
        cursor = sqlite_connection.cursor()
        print("Connection established with SQLite database: " + database_name)


        # Creates Card table
        card_table_query = '''CREATE TABLE IF NOT EXISTS cards (
            card_id TEXT PRIMARY KEY,
            rarity TEXT NOT NULL,
            card_type TEXT NOT NULL,
            card_set TEXT NOT NULL,
            name TEXT NOT NULL,
            power INTEGER,
            counter INTEGER,
            text TEXT,
            life INTEGER, 
            cost INTEGER,
            trigger TEXT
        )
        '''
        cursor.execute(card_table_query)
        sqlite_connection.commit()

        # Creates color tables for one-to-many relationships
        color_bridge_query = '''CREATE TABLE IF NOT EXISTS colors(
            color_name TEXT PRIMARY KEY
        )'''
        cursor.execute(color_bridge_query)
        sqlite_connection.commit()

        color_cards_query = '''CREATE TABLE IF NOT EXISTS color_cards(
            card_id TEXT,
            color_name TEXT,
            PRIMARY KEY (card_id, color_name),
            FOREIGN KEY (card_id) REFERENCES cards(card_id),
            FOREIGN KEY (color_name) REFERENCES colors(color_name)
        )'''
        cursor.execute(color_cards_query)
        sqlite_connection.commit()

        # Creates attribute tables for one-to-many relationships
        attribute_bridge_query = '''CREATE TABLE IF NOT EXISTS attributes(
            attribute_name TEXT PRIMARY KEY
        )'''
        cursor.execute(attribute_bridge_query)
        sqlite_connection.commit()

        attribute_cards_query = '''CREATE TABLE IF NOT EXISTS attribute_cards(
            card_id TEXT,
            attribute_name TEXT,
            PRIMARY KEY (card_id, attribute_name),
            FOREIGN KEY (card_id) REFERENCES cards(card_id),
            FOREIGN KEY (attribute_name) REFERENCES attributes(attribute_name)
        )'''
        cursor.execute(attribute_cards_query)
        sqlite_connection.commit()

        # Creates feature tables for one-to-many relationships
        feature_bridge_query = '''CREATE TABLE IF NOT EXISTS features(
            feature_name TEXT PRIMARY KEY
        )'''
        cursor.execute(feature_bridge_query)
        sqlite_connection.commit()

        feature_cards_query = '''CREATE TABLE IF NOT EXISTS feature_cards(
            card_id TEXT,
            feature_name TEXT,
            PRIMARY KEY (card_id, feature_name),
            FOREIGN KEY (card_id) REFERENCES cards(card_id),
            FOREIGN KEY (feature_name) REFERENCES features(feature_name)
        )'''
        cursor.execute(feature_cards_query)
        sqlite_connection.commit()

        # Open json and load information into database.
        f = open(json_name)
        data = json.load(f)

        # Load next card into database. Currently incomplete.
        for i in data:
            next_card = data[i]
            query_stem = "INSERT OR IGNORE INTO cards (card_id, rarity, card_type, card_set, name"
            values_stem = "VALUES("
            values_stem += "\"" +str(next_card['card_id']) + "\", \""  + str(next_card['rarity']) + "\", \"" + next_card['card_type'] + "\", \"" + next_card['card_set'] + "\", \"" + next_card['name'].replace("\'", "\'\'").replace("\"", "\"\"") + "\""
            
            # Give a card power if it has one.
            if 'power' in next_card:
                if next_card['power'] != '':
                    query_stem += ", power"
                    values_stem += ", \"" + next_card['power'].replace("\'", "\'\'").replace("\"", "\"\"") + "\""

            # Give a card a counter effect if it has one.
            if 'counter' in next_card:
                if next_card['counter'] != '':
                    query_stem += ", counter"
                    values_stem += ", " + next_card['counter']
            
            # Give a card text if it has text
            if 'text' in next_card:
                if next_card['text'] != '':
                    query_stem += ", text"
                    values_stem += ", \"" + next_card['text'].replace("\'", "\'\'").replace("\"", "\"\"") + "\""

            # Give a card a life value if it has one.
            if 'life' in next_card:
                if next_card['life'] != '':
                    query_stem += ", life"
                    values_stem += ", " + next_card['life']

            # Add card cost
            if 'cost' in next_card:
                if (next_card['cost'] != '') & (next_card['cost'] != '-'):
                    query_stem += ", cost"
                    values_stem += ", " + str(next_card['cost'])
            

            # Add card trigger
            if 'trigger' in next_card:
                if next_card['trigger'] != '':
                    query_stem += ", trigger"
                    values_stem += ", \"" + next_card['trigger'].replace("\'", "\'\'").replace("\"", "\"\"") + "\""
            query_stem += ")"
            values_stem += ")"

            print(query_stem + values_stem)
            cursor.execute(query_stem + values_stem)
            sqlite_connection.commit()
            print("Success!")
            # Add attributes and connect one-to-many relationships.
            for attribute in next_card['attribute']:
                if attribute != '':
                    attribute_creation_query = f"INSERT OR IGNORE INTO attributes (attribute_name) VALUES (\"{attribute}\")"
                    cursor.execute(attribute_creation_query)
                    attribute_link_query = f"INSERT OR IGNORE INTO attribute_cards (card_id, attribute_name) VALUES (\"{next_card['card_id']}\", \"{attribute}\")"
                    cursor.execute(attribute_link_query)
                    sqlite_connection.commit()
            
            for color in next_card['color']:
                if color != '':
                    color_creation_query = f"INSERT OR IGNORE INTO colors (color_name) VALUES (\"{color}\")"
                    cursor.execute(color_creation_query)
                    color_link_query = f"INSERT OR IGNORE INTO color_cards (card_id, color_name) VALUES (\"{next_card['card_id']}\", \"{color}\")"
                    cursor.execute(color_link_query)
                    sqlite_connection.commit()

            for feature in next_card['feature']:
                if feature != '':
                    feature_creation_query = f"INSERT OR IGNORE INTO features (feature_name) VALUES (\"{feature}\")"
                    cursor.execute(feature_creation_query)
                    feature_link_query = f"INSERT OR IGNORE INTO feature_cards (card_id, feature_name) VALUES (\"{next_card['card_id']}\", \"{feature}\")"
                    cursor.execute(feature_link_query)
                    sqlite_connection.commit()


        
            
            
        sqlite_connection.commit()
        cursor.close()
        print("Connection closed with database: " + database_name)
    except sqlite3.Error as error:
        print("Error occurred - " + str(error))




build_sqlite('asia-cardlist.json', 'asia-cards.db')