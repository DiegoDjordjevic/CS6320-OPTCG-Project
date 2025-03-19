from bs4 import BeautifulSoup
import os
import re

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
                print(infoCol.text)
                name = cardName.text
                #removes Cost prefix for characters, events, and stages, as well as removes Life prefix for Leaders
                cost = backCol.find('div', class_='cost').text.removeprefix('Cost').removeprefix('Life')
                #removes everything except the actual attribute itself
                attribute = backCol.find('div', class_='attribute').text.removeprefix('\nAttribute\n').removesuffix('\n')
                #removes Power prefix and leaves only the power value itself
                power = backCol.find('div', class_='power').text.removeprefix('Power')
                #removes Counter prefix and leaves only the counter value itself
                counter = backCol.find('div', class_='counter').text.removeprefix('Counter')
                #removes Color prefix and leaves only the color itself
                color = backCol.find('div', class_='color').text.removeprefix('Color')
                #removes Type prefix and leaves just the type itself
                feature = backCol.find('div', class_='feature').text.removeprefix('Type')
                #removes Effect prefix leaving only the effects themselves
                text = backCol.find('div', class_='text').text.removeprefix('Effect')
                print(name)
                print([cost, attribute, power, counter, color, feature, text])
                print()
                break
            break
        #print(infoCols)


