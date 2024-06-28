import requests
import pandas as pd
import matplotlib.pyplot as plt
import circlify
import matplotlib.image as mpimg
from PIL import Image, ImageDraw
import json

RIOT_API_KEY="RGAPI-c0840e05-d32b-47fc-8e38-2fc6b060d3c7"

def circular_crop(image_path):
    # Open the input image
    img = Image.open(image_path).convert("RGBA")
    # Create same size alpha layer with circle
    alpha = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(alpha)
    draw.pieslice([0, 0, img.size[0], img.size[1]], 0, 360, fill=255)
    # Composite the alpha layer onto the RGBA image
    img.putalpha(alpha)
    # Create a new image with white background to paste the circle onto
    bg = Image.new("RGBA", img.size, (255, 255, 255, 0))
    bg.paste(img, (0, 0), img)
    return bg

def createBubbleChart2(df):
    # Compute circle positions
    circles = circlify.circlify(
        df['Value'].tolist(),
        show_enclosure=False,
        target_enclosure=circlify.Circle(x=0, y=0, r=1)
    )

    # Reverse the order of the circles to match the order of data
    circles = circles[::-1]

    # Create just a figure and only one subplot
    fig, ax = plt.subplots(figsize=(10, 10))

    # Title
    ax.set_title('Basic circular packing')

    # Remove axes
    ax.axis('off')

    # Find axis boundaries
    lim = max(
        max(
            abs(circle.x) + circle.r,
            abs(circle.y) + circle.r,
        )
        for circle in circles
    )
    plt.xlim(-lim, lim)
    plt.ylim(-lim, lim)

    # List of labels and images
    labels = df['Name']
    images = df['Images']

    # Print circles with images
    for circle, label, image_path in zip(circles, labels, images):
        x, y, r = circle
        # Load the image
        
        # Circular crop the image
        img = circular_crop(image_path)
        # Resize the image to fit the circle diameter
        img = img.resize((int(2*r*300), int(2*r*300)), Image.Resampling.LANCZOS)
        # Place the image inside the circle
        img_extent = [x-r, x+r, y-r, y+r]
        ax.imshow(img, extent=img_extent, aspect='auto', alpha=1)
        # Draw the circle outline
        ax.add_patch(plt.Circle((x, y), r, alpha=0.2, linewidth=2, edgecolor='black', fill=False))
        # Add the label
        plt.annotate(
            label,
            (x, y),
            va='center',
            ha='center'
        )

    plt.savefig('packed_bubble_chart_with_images.png', dpi=300, bbox_inches='tight')

def getPuuid(accountName, tagLine):
    headers = {
        "X-Riot-Token": RIOT_API_KEY
    }

    url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{accountName}/{tagLine}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:    
        data = response.json()
        return data['puuid']
    else:
        return ""
    
def getChampionMastery(puuid):
    headers = {
        "X-Riot-Token": RIOT_API_KEY
    }

    url = f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:    
        data = response.json()
        return data
    else:
        return []

def generateChampIdtoNameMap(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        json_data = f.read()
        # print(json_data)

    data = json.loads(json_data)
    
    map = {}

    for champ_name, champ_data in (data['data']).items():
        map[int(champ_data['key'])] = champ_name

    return map

def generatePackedBubbleChart(accountName, tagLine):
    puuid = getPuuid(accountName, tagLine)

    champMastery = getChampionMastery(puuid)

    idToNameMap = generateChampIdtoNameMap("champion.json")

    champions = []
    values = []
    images = []
    for item in champMastery:
        
        values.append(item['championPoints'])
        id = item['championId']
        # print(type(id))
        champions.append(id)
        name = idToNameMap.get(id, None)

        images.append(f"champion/splash/{name}_0.jpg")

    df = pd.DataFrame({
    'Name': champions,
    'Value': values,
    'Images': images
    })

    createBubbleChart2(df)

generatePackedBubbleChart('ARamenBowl', 'NA1')
