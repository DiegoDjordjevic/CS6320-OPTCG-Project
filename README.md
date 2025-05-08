This project is meant to be a trading card generator based on the One Piece Trading Card Game (OPTCG). If youre looking to generate fun unique new cards to play with friends or balanced cards that could be played in competitive matches this is the tool for you.

HOW TO RUN:

TO INSTALL ALL REQUIREMENTS:
    - Run the command 'pip install -r requirements.txt'

TO DOWNLOAD AN UPDATED CARDLIST:
    - Download the cardlist by running 'python download_cardlists.py'
    - This will open a browser instance that will manually scrape the OPTCG website for every current playable card, creating a series of HTML files corresponding
    to each card. These can be found in a folder titled 'Asia-Cardlists'.

TO EXTRACT JSON FROM HTML FILES:
    - First, obtain the HTML data for each card by running download_cardlists.py (see above).
    - Run 'extract_json.py'
    - This will create a .json file called 'extract_json.py', containing detailed information about each card in the dataset extracted by download_cardlists.py.

TO BUILD SQLITE DATABASE OF EACH CARD:
    - Run build_database.py
    - This will either update or build a new database "asia-cards.db" based in SQLite using Python's built-in SQLite functionality.
    - To completely refresh the database, delete asia-cards.db from the directory then rerun build_databse.py

TO BUILD CHROMADB VECTOR STORE:
    - Run build_vector_store.py
    - This will create the ChromaDB database locally, and insert all cards into it.

TO CREATE CARDS:    
    - Create a .env file in the project directory containing a Google Gemini api key in the following format.
        GOOGLE_API_KEY='your key'
    - This program will not run without the API key.
    - Run create_cards.py. The program will prompt you step-by-step to generate an original card of a chosen type. It runs entirely within the terminal. 
