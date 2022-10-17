import json
import textwrap
import re
from PIL import Image, ImageFont, ImageDraw
import nltk.tokenize

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


for i in range(1,len(screenshot_text_map)):

    current_image = screenshot_text_map[i][1]

    title_font = ImageFont.truetype('Roboto/Roboto-Black.ttf',100)

    title_text = screenshot_text_map[i][2]

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

    current_image = Image.open(current_image).convert("RGBA")
    black_image_background = Image.new("RGBA", current_image.size, "BLACK")
    black_image_background.paste(current_image, mask=current_image)

    current_image = black_image_background.convert("RGBA")

    image_editable = ImageDraw.Draw(current_image)
    current_image.save("outputImage/"+screenshot_text_map[i][0]+".png")
    current_image=current_image.resize((900,2000))


    curr_img_w, curr_img_h = current_image.size
    background = Image.open('background_phone_border.png')
    bg_w , bg_h = background.size
    offset = ((bg_w-curr_img_w)//2,(bg_h-curr_img_h)//2)
    background.paste(current_image,offset,current_image)


    image_editable = ImageDraw.Draw(background)
    output_text = textwrap.fill(text=output_text,width = 60)
    _, _, w, h = image_editable.textbbox((0, 0), output_text, font=title_font)
    width_position = ((bg_w * 20) / 100)
    image_editable.text(((bg_w - w) / 2, 300), output_text, (255, 255, 255), font=title_font)
    background.convert("RGB").save("UpdatedImages/" + screenshot_text_map[i][0] + ".jpeg")

