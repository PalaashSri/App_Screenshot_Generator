'''
Name: Palaash Srivastava
Student ID: 30004292
Script for performing Google Play store scraping and obtaining the required information and performing further analysis
using POS tagging.

First the Google Play scraper package needs to be downloaded from : https://github.com/digitalmethodsinitiative/google-play-scraper
and placed at a location where it can be imported by this script. Please note that the google-play-scraper package was
modified in this project to obtain app screenshots. That change has not been uploaded to github because it is a minor
change and most of the package is still the same.

There are comments in the code below which inform the process being performed by that code.
'''

'''
Line 16 - 23 Importing packages that are required to perform tasks. Line 16 is importing the google-play-scraper package
that is downloaded as instructed above.
'''
from google_play_scraper.scraper import PlayStoreScraper
import wget
import os
import pytesseract
from PIL import Image
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

'''
Line 29 - 30 Setting some global variable. Line 30 is required when working with pytesseract. Download instructions for 
pytesseract have been mentioned in the readme file.
'''
image_dataset_file_name = "imageUrlDatabase.txt"
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

def appstore_scraper(app_name):
    '''
    Given an app name this function utilizes the google-play-scraper package and its functions to get information about
    that app and other similar apps. For our analysis, we only require the app screenshots which are stored in
    image_dataset array (the array here stores url where the app screenshots are located) and app description under
    description_dataset.
    :param app_name: Application name on Google Play store. Like Spotify.
    :return: Dataset of app screenshots and app description.
    '''
    scraper = PlayStoreScraper()
    results = scraper.get_app_ids_for_query(app_name,country="US",lang="en")
    similar = scraper.get_similar_app_ids_for_app(results[0],country="US",lang="en")

    app_details, image_dataset, description_dataset = scraper.get_multiple_app_details(similar,country="US",lang="en")
    return image_dataset, description_dataset

def create_image_url_dataset(image_dataset):
    '''
    Given a dataset of app screenshots url, this function opens a text document which stores the url of all the app
    screenshots scraped from the Google Play store.
    :param image_dataset:
    :return: None
    '''
    image_url_database = open("imageUrlDatabase.txt","a")
    image_oned_array = []
    for i in range(len(list(image_dataset))):
        for value in list(image_dataset[i]):
            image_oned_array.append(value)

    for values in image_oned_array:
        image_url_database.write(values)
        image_url_database.write("\n")
    image_url_database.close()

def create_description_dataset(description_dataset):
    '''
    Given a dataset of app description, this function updates a text file which stores important description content
    for all the apps scraped on Google Play store.
    :param description_dataset:
    :return: None
    '''
    app_description_database = open("appDescriptionDatabase.txt","a",encoding='utf-8')
    tokenize_dataset = []
    '''
    Line 81 - 88 perform preprocessing on the app description obtained to remove unwanted characters and only retain 
    information related to features present in an app. 
    '''
    for i in range(len(description_dataset)):
        value = description_dataset[i]
        value = re.sub('[!@#$●&•]','',value)
        value = value.replace('<br>','')
        value = re.sub(r'http\S+', '', value)
        value = re.sub(r'www\S+', '', value)
        tokenize_dataset.append(sent_tokenize(value))
        description_dataset[i] = value

    '''
    Lines 94 - 98 Writing the important feature information obtained after performing the above pre processing steps to
    the appDescriptionDatabase.txt file.
    '''
    for values in tokenize_dataset:
        for chars in values:
            app_description_database.write(chars)
            app_description_database.write("\n")
    app_description_database.close()

def create_concise_feature_description():
    '''
    The previous create_description_dataset only performs pre processing where general information from app description
    is removed to obtain feature related sentences.
    This function performs further pre processing and pos tagging to only obtain text that is directly related to
    features like "click photo" etc. This specific information is stored in appDescriptionDatabase.txt
    :return: None
    '''
    with open("appDescriptionDatabase.txt",encoding='utf-8') as file:
        for line in file:

            '''
            Lines 115 - 120 perform further pre processing.
            '''
            line = line.lower()
            line = line.replace("<b>","")
            line=line.replace("</b>","")
            line = re.sub('[⭐%❻*❤✔🔐”]', '', line)
            line = word_tokenize(line)
            pos_array = nltk.pos_tag(line)

            '''
            Lines 125 - 131 use pos tagging to only obtain words which will provide specific information related to 
            features. This process is based on the paper:
            Johann, Timo, Stanik, Christoph, Alizadeh B, Alireza M, & Maalej, Walid. (2017). SAFE: A Simple Approach for 
            Feature Extraction from App Descriptions and App Reviews. 2017 IEEE 25th International Requirements 
            Engineering Conference (RE), 21–30. https://doi.org/10.1109/RE.2017.71
            '''
            for i in range(len(pos_array)-1):
                if pos_array[i][1]=="NN" and pos_array[i+1][1]=="NN":
                    print(pos_array[i][0]+" "+pos_array[i+1][0])
                elif pos_array[i][1]=="VB" and pos_array[i+1][1]=="NN":
                    print(pos_array[i][0]+" "+pos_array[i+1][0])
                elif pos_array[i][1] == "ADJ" and pos_array[i + 1][1] == "NN":
                    print(pos_array[i][0] + " " + pos_array[i + 1][0])



def image_downloader():
    '''
    This function performs the task of downloading app screenshots whose urls are stored in imageUrlDatabase.txt file.
    These images are stored in image_dataset folder.
    :return: None
    '''
    image_counter = 0
    with open(image_dataset_file_name) as file:
        for line in file:
            print(line.rstrip())
            image_filename = wget.download(line,out="image_dataset/")
            upadated_name = "image_dataset/app_screenshot_"+str(image_counter)+".png"
            os.rename(image_filename,upadated_name)
            print('Image Successfully Downloaded: ', upadated_name)
            image_counter+=1

def image_text_dataset():
    '''
    This function is used to perform analysis on the text descriptions of the obtained app screenshots and understand
    their word structure.
    :return: None
    '''
    image_text_database = open("imageTextDatabase.txt", "w")
    pos_tag_dictionary = {}

    # For all the images in the image_dataset folder.
    for i in range(617):
        #Pytesseract image_to_string function returns the screen text on a given image.
        obj = pytesseract.image_to_string(Image.open('image_dataset/app_screenshot_'+str(i)+'.png'))

        '''
        Lines 172 - 184 We are performing pre processing on the screen text obtained to try only retain information that 
        is text description and not the text that is present on the app screenshot part. We further remove unwanted 
        characters from the text retained. 
        '''
        obj = obj.strip('\t')
        obj = obj.split('\n')
        obj = [i for i in obj if i]
        obj = obj[:3]
        for k in range(len(obj)):
            values=obj[k]
            values = re.sub(r"([!.?])", r" \1", values)
            values = re.sub(r"[^a-zA-Z!.?]+", r" ", values)
            values = re.sub(r"\s+", " ", values)
            values = values.lower()
            obj[k] = values
        if len(obj)==0:
            continue

        '''
        Pos tagging is performed on the words obtained from above and this pos tagging is added to a dictionary called
        pos_tag_dictionary. This is performed to understand the widely used structure of word formation for text 
        description in app screenshots. 
        '''
        pos_tag_array = nltk.pos_tag(obj)
        pos_tag_key = ""
        print(obj)

        for index in range(len(pos_tag_array)):
            pos_tag_key+=pos_tag_array[index][1]+","
        pos_tag_key = pos_tag_key.rstrip(",")
        if pos_tag_dictionary.get(pos_tag_key)==None:
            pos_tag_dictionary[pos_tag_key]=1
        else:
            pos_tag_dictionary[pos_tag_key] = pos_tag_dictionary.get(pos_tag_key)+1
        image_text_database.write(str(obj))
        image_text_database.write("\n")

    '''
    Lines 211 - 213 Sort the dictionary and print the contents of the dictionary so that we can easily analyse the most 
    used word formation for text description in app screenshots that are currently listed in Google Play store. 
    '''
    image_text_database.close()
    sorted_dictionary = {k: v for k, v in sorted(pos_tag_dictionary.items(), key = lambda item:item[1])}
    print(pos_tag_dictionary)
    print(sorted_dictionary)


#Lines 219 - 226 list the function calls. These are currently commented so that they are not accidently run because of
#clicking the run button. To run the script, below comment symbol on line 219 and 228 can be removed.
'''
list_of_apps = ["Spotify","Chrome","Microsoft Teams","Google Translate","Sketchbook","Amazon","BBC","BasicNote - Notes, Notepad","WeNote: Notes Notebook Notepad","Smart Note - Notes, Notepad"]
for apps in list_of_apps:
    image_dataset, description_dataset = appstore_scraper(apps)
    create_description_dataset(description_dataset)
    create_image_url_dataset(image_dataset)
    image_downloader()
    create_concise_feature_description()
image_text_dataset()
'''