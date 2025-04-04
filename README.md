This project is meant to be a trading card generator based on the One Piece Trading Card Game (OPTCG). If youre looking to generate fun unique new cards to play with friends or balanced cards that could be played in competitive matches this is the tool for you.

HOW TO RUN:
    TO DOWNLOAD AN UPDATED CARDLIST:
    - Install Selenium using 'pip install selenium'
    - Download the cardlist by running 'python download_cardlists.py'
    - This will open a browser instance that will manually scrape the OPTCG website for every current playable card, creating a series of HTML files corresponding
    to each card. These can be found in a folder titled 'Asia-Cardlists'.

    TO EXTRACT JSON FROM HTML FILES:
    - First, obtain the HTML data for each card by running download_cardlists.py (see above).
    - Run 'extract_json.py'
    - This will create a .json file called 'extract_json.py', containing detailed information about each card in the dataset extracted by download_cardlists.py.

Next Steps:
Have an automatic check for the downloaded cardlists and the extracted data.
Possibly ignore SP Cards so that the original rarities for cards are kept.
