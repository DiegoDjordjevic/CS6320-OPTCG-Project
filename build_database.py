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
            text TEXT NOT NULL,
            life INTEGER, 
            cost INTEGER NOT NULL,
            trigger TEXT
        )
        '''
        cursor.execute(card_table_query)

        # Creates color tables for one-to-many relationships
        color_bridge_query = '''CREATE TABLE IF NOT EXISTS colors(
            color_name TEXT PRIMARY KEY
        )'''
        cursor.execute(color_bridge_query)

        color_cards_query = '''CREATE TABLE IF NOT EXISTS color_cards(
            card_id TEXT,
            color_name TEXT,
            PRIMARY KEY (card_id, color_name),
            FOREIGN KEY (card_id) REFERENCES cards(card_id),
            FOREIGN KEY (color_name) REFERENCES colors(color_name)
        )'''
        cursor.execute(color_cards_query)

        # Creates attribute tables for one-to-many relationships
        attribute_bridge_query = '''CREATE TABLE IF NOT EXISTS attributes(
            attribute_name TEXT PRIMARY KEY
        )'''
        cursor.execute(attribute_bridge_query)

        attribute_cards_query = '''CREATE TABLE IF NOT EXISTS attribute_cards(
            card_id TEXT,
            attribute_name TEXT,
            PRIMARY KEY (card_id, attribute_name),
            FOREIGN KEY (card_id) REFERENCES cards(card_id),
            FOREIGN KEY (attribute_name) REFERENCES attributes(attribute_name)
        )'''
        cursor.execute(attribute_cards_query)

        # Creates feature tables for one-to-many relationships
        feature_bridge_query = '''CREATE TABLE IF NOT EXISTS features(
            feature_name TEXT PRIMARY KEY
        )'''
        cursor.execute(feature_bridge_query)

        feature_cards_query = '''CREATE TABLE IF NOT EXISTS feature_cards(
            card_id TEXT,
            feature_name TEXT,
            PRIMARY KEY (card_id, feature_name),
            FOREIGN KEY (card_id) REFERENCES cards(card_id),
            FOREIGN KEY (feature_name) REFERENCES features(feature_name)
        )'''

        # Open json and load information into database.
        f = open(json_name)
        data = json.load(f)

        # Load next card into database. Currently incomplete.
        for i in data:
            next_card = data[i]
            query_stem = "INSERT OR IGNORE INTO cards (card_id, rarity, card_type, card_set, name"
            values_stem = "VALUES("
            values_stem += str(next_card['card_id']) + ", " + str(next_card['rarity']) + next_card['card_type'] + ", " + next_card['card_set'] + next_card['name']
            if (next_card['power'] != ''):
                query_stem += ", power"
                values_stem += ", " + next_card['power']

            if (next_card['counter'] != ''):
                query_stem += ", counter"
                values_stem += ", " + next_card['counter']
            

            # Check for features and add any new features to the database
            card_features = next_card['feature']
            
            

        cursor.close()
        print("Connection closed with database: " + database_name)
    except sqlite3.Error as error:
        print("Error occurred - " + str(error))




build_sqlite('asia-cardlist.json', 'asia-cards.db')