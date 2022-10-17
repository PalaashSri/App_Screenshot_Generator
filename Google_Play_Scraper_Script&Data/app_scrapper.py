from google_play_scraper.scraper import PlayStoreScraper
import wget
import os
import pytesseract
from PIL import Image
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

image_dataset_file_name = "imageUrlDatabase.txt"
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

def appstore_scraper(app_name):
    scraper = PlayStoreScraper()
    results = scraper.get_app_ids_for_query(app_name,country="US",lang="en")
    similar = scraper.get_similar_app_ids_for_app(results[0],country="US",lang="en")

    app_details, image_dataset, description_dataset = scraper.get_multiple_app_details(similar,country="US",lang="en")
    return image_dataset, description_dataset

def create_image_url_dataset(image_dataset):
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
    app_description_database = open("appDescriptionDatabase.txt","a",encoding='utf-8')
    print(len(description_dataset))
    tokenize_dataset = []
    for i in range(len(description_dataset)):
        value = description_dataset[i]
        value = re.sub('[!@#$●&•]','',value)
        value = value.replace('<br>','')
        value = re.sub(r'http\S+', '', value)
        value = re.sub(r'www\S+', '', value)
        tokenize_dataset.append(sent_tokenize(value))
        description_dataset[i] = value
    for values in tokenize_dataset:
        for chars in values:
            app_description_database.write(chars)
            app_description_database.write("\n")
    app_description_database.close()

def create_concise_feature_description():
    with open("appDescriptionDatabase.txt",encoding='utf-8') as file:
        for line in file:
            line = line.lower()
            line = line.replace("<b>","")
            line=line.replace("</b>","")
            line = re.sub('[⭐%❻*❤✔🔐”]', '', line)
            line = word_tokenize(line)
            pos_array = nltk.pos_tag(line)
            #print(pos_array[1][1])
            for i in range(len(pos_array)-1):
                if pos_array[i][1]=="NN" and pos_array[i+1][1]=="NN":
                    print(pos_array[i][0]+" "+pos_array[i+1][0])
                elif pos_array[i][1]=="VB" and pos_array[i+1][1]=="NN":
                    print(pos_array[i][0]+" "+pos_array[i+1][0])
                elif pos_array[i][1] == "ADJ" and pos_array[i + 1][1] == "NN":
                    print(pos_array[i][0] + " " + pos_array[i + 1][0])



def image_downloader():
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
    image_text_database = open("imageTextDatabase.txt", "w")
    pos_tag_dictionary = {}
    for i in range(617):
        obj = pytesseract.image_to_string(Image.open('image_dataset/app_screenshot_'+str(i)+'.png'))
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

    image_text_database.close()
    sorted_dictionary = {k: v for k, v in sorted(pos_tag_dictionary.items(), key = lambda item:item[1])}
    print(pos_tag_dictionary)
    print(sorted_dictionary)

'''
list_of_apps = ["Spotify","Chrome","Microsoft Teams","Google Translate","Sketchbook","Amazon","BBC","BasicNote - Notes, Notepad","WeNote: Notes Notebook Notepad","Smart Note - Notes, Notepad"]
for apps in list_of_apps:
    image_dataset, description_dataset = appstore_scraper(apps)
    create_description_dataset(description_dataset)
    create_image_url_dataset(image_dataset)
    image_downloader()
    image_text_dataset()
    create_concise_feature_description()
'''