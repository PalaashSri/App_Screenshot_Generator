'''
Name: Palaash Srivastava
Student ID: 30004292
Script for Automated Screenshot Generation

First the droidbot package needs to be downloaded from: https://github.com/honeynet/droidbot
The steps to run Droidbot have been mentioned in the github page.
After setting up Droidbot and placing the apk file (Notepad app) the following command was run using terminal
droidbot -a Notepad.apk -o output_dir -timeout 4000 -grant_perm -is_emulator -ignore_ad
Detail on the above command can be obtained by writing droidbot -h in the terminal at Droidbot install location.

Once the process is completed, in the output folder (in above command called output_dir) there will be a js file called
utg.js. This file contains information about each screen captured. This file needs to be converted to json file called
utg.json so that this script can obtain information from it.

This script needs to be placed such that it can access the output folder and its contents created by Droidbot.

There are comments in the code below which inform the process being performed by that code.
'''


'''
Line 25-29 Importing the required packages. 
'''
import json
import textwrap
import re
from PIL import Image, ImageFont, ImageDraw
import nltk.tokenize


'''
Line 35 - 51
We firstly open utg.json file which contains information about all the screens captured by droidbot.
We then load this json information in jsonObject and iterate through the nodes and add the needed information like 
id, image path and text to an array called screenshot_text_map
'''
with open("utg.json") as jsonFile:
    jsonObject = json.load(jsonFile)
    jsonFile.close()

nodes = jsonObject['nodes']
num_nodes = jsonObject['num_nodes']

screenshot_text_map = []

screenshot_text_map.append(["id","image","text"])

for item in nodes:
    id = item['id']
    image = item['image']
    content_split = item['content'].split('\n')
    text = content_split[len(content_split)-1]
    screenshot_text_map.append([id,image,text])


'''
For each node in screenshot_text_map we go through this loop which generate the screenshot.
'''
for i in range(1,len(screenshot_text_map)):

    '''
    Line 65 - 67 We extract information from the array and store it in variables.
    '''
    current_image = screenshot_text_map[i][1]
    title_font = ImageFont.truetype('Roboto/Roboto-Black.ttf',100)
    title_text = screenshot_text_map[i][2]

    '''
    Line 72 - 82 performs pre processing on the screen text obtained from Droidbot. This preprocessing is important to 
    remove unwanted characters and only obtain important feature related words.
    '''
    title_text = title_text.replace('"HelloWorld"',"")
    title_text = title_text.replace('<Untitled>',"")
    title_text = re.sub(r"[^a-zA-Z!.?,]+", r" ", title_text)
    title_text = re.sub('[!@#$●&•]', '', title_text)
    title_text = re.sub(r'http\S+', '', title_text)
    title_text = re.sub(r'www\S+', '', title_text)
    list_of_text = title_text.split(",")
    for j in range(len(list_of_text)):
        list_of_text[j] = list_of_text[j].lower()
    list_of_text = [i for i in list_of_text if i]

    '''
    Line 87 - 96 We retrieve the pos tag values for the words obtained after above pre processing. 
    Based on the rules built from analysis on current app store screenshots, the text that should contain important 
    feature information are added to the output text. The rule can be seen in line 93 and 95. 
    '''
    in_hand_text = ""
    output_text = ""
    tagged = nltk.pos_tag(list_of_text)
    for k in range(len(tagged)):
        if tagged[k][1]=="NN" and tagged[k][0] == "search...":
            output_text = tagged[k][0] + " " + output_text
        elif (tagged[k][1] == "NN" or tagged[k][1] == "NNS" or tagged[k][1] == "VB" or tagged[k][1] == "VBP") and (
                len(tagged[k][0]) < 20):
            output_text+=tagged[k][0] + ","
    output_text=output_text.rstrip(",")

    '''
    Line 103 - 111 The app screenshot captured by Droidbot is obtained and updated to have black background. 
    '''
    current_image = Image.open(current_image).convert("RGBA")
    black_image_background = Image.new("RGBA", current_image.size, "BLACK")
    black_image_background.paste(current_image, mask=current_image)

    current_image = black_image_background.convert("RGBA")

    image_editable = ImageDraw.Draw(current_image)
    current_image.save("outputImage/"+screenshot_text_map[i][0]+".png")
    current_image=current_image.resize((900,2000))

    '''
    Line 116 - 120 The phone border at file background_phone_border.png is added to the screenshots to provide realistic 
    phone screenshot view. 
    '''
    curr_img_w, curr_img_h = current_image.size
    background = Image.open('background_phone_border.png')
    bg_w , bg_h = background.size
    offset = ((bg_w-curr_img_w)//2,(bg_h-curr_img_h)//2)
    background.paste(current_image,offset,current_image)

    '''
    Line 126 - 131 The text description generated from line 87-96 is combined with the background app screenshot image
    to generate the final app screenshot that can be listed in an app store. This image is saved to App_Screenshots
    folder in jpeg format. 
    '''
    image_editable = ImageDraw.Draw(background)
    output_text = textwrap.fill(text=output_text,width = 60)
    _, _, w, h = image_editable.textbbox((0, 0), output_text, font=title_font)
    width_position = ((bg_w * 20) / 100)
    image_editable.text(((bg_w - w) / 2, 300), output_text, (255, 255, 255), font=title_font)
    background.convert("RGB").save("App_Screenshots/" + screenshot_text_map[i][0] + ".jpeg")

