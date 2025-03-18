from bs4 import BeautifulSoup
import os
cardlist_path = 'Cardlists'
for filename in os.listdir(cardlist_path):
    with open(os.path.join(cardlist_path, filename), 'r') as f:
        soup = BeautifulSoup(f, 'html.parser')
        


