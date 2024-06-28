import requests
import time
import pandas as pd
import datetime
import time
import os

RIOT_API_KEY = os.environ("RIOT_API_KEY")
HEADER = {"X-Riot-Token": RIOT_API_KEY}

LAST_PATCH_DATE = datetime.datetime(2024, 5, 14)
LAST_PATCH_TIME = int(LAST_PATCH_DATE.timestamp())

BASE_API_URL = "https://na1.api.riotgames.com"

RANKED_QUEUE_ID = 420 
BLUE_SIDE_TEAM_ID = 100
RED_SIDE_TEAM_ID = 200

def getResponse(url):
    response = requests.get(url, headers=HEADER)
    
    if response.status_code == 200:
        data = response.json()
        return data
    elif response.status_code == 429:
        data = response.json()
        if "Retry-After" in response.headers:
            retry_after = int(response.headers["Retry-After"])
            print(f"Retrying in {retry_after} seconds")
            time.sleep(retry_after)
            response = requests.get(url, headers=HEADER)
            return response.json()
        else:
            print("exponential backoff")
            # exponential backoff
            for i in range(5):  # Retry up to 5 times
                time.sleep(2 ** (i+2))  # Exponential backoff
                response = requests.get(url, headers=HEADER)
                if response.status_code == 200:
                    data = response.json()
                    return data
                elif response.status_code != 429:
                    break
    else:
        print(response.status_code)
        return None

def getChallengerQ():
    url = f"{BASE_API_URL}/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5"

    response = getResponse(url)
    if response is None:
        print("None2")
        return None
    else:
        return response

def convertSummonerIdsToPuuids(ids):
    puuids = []
    for id in ids:
        url = f"{BASE_API_URL}/lol/summoner/v4/summoners/{id}"

        response = getResponse(url)
        if response is None:
            continue
        
        puuids.append(response['puuid'])
        break

    return puuids

def getMatchIds(ids):
    matchIds = set()
    for id in ids:
        # url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{id}/ids?type=ranked&start=0&count=100"
        url = f"{BASE_API_URL}/lol/match/v5/matches/by-puuid/{id}/ids?queue={RANKED_QUEUE_ID}&type=ranked&start={LAST_PATCH_TIME}&count=100"
        print(url)
        response = getResponse(url)
        if response is None:
            continue
        
        r = set(response)
        matchIds = matchIds.union(r)
        
    return matchIds

def getMatchData(ids):
    
    winning_team = []
    blue_side_champs = []
    red_side_champs = []
    blue_side_bans = []
    red_side_bans = []

    
    # TODO
    # Get Champs banned, champs picked, which team won,
    for id in ids:
        url = f"{BASE_API_URL}/lol/match/v5/matches/{id}"

        response = getResponse(url)

        if response is None:
            continue
        
        response = response['info']
        # Make sure game was completed
        if response['endOfGameResult'] != "GameComplete":
            continue
        
        # Skip remakes
        if response['gameDuration'] <= 240:
            continue
        
        teamsData = response['teams'] 
        participantsData = response['participants'] # data is blue side players then red side

        # print(teamsData)
        # print("----------------")
        # print(participantsData)

        blue_side_win = teamsData[0]['win']
        winning_team.append(blue_side_win) # this is blue-side win/lose

        blue_champs = [player['championId'] for player in participantsData if player['teamId'] == BLUE_SIDE_TEAM_ID]
        red_champs =  [player['championId'] for player in participantsData if player['teamId'] == RED_SIDE_TEAM_ID]

        blue_side_champs.append(blue_champs)
        red_side_champs.append(red_champs)

        blue_side_data = teamsData[0]['bans']
        red_side_data = teamsData[1]['bans']
        blue_bans = [ban['championId'] for ban in blue_side_data]
        red_bans = [ban['championId'] for ban in red_side_data]

        blue_side_bans.append(blue_bans)
        red_side_bans.append(red_bans)
    
    df = pd.DataFrame({
    'Win': winning_team,
    'Blue Side Bans': blue_side_bans,
    'Red Side Bans': red_side_bans,
    'Blue Side Champions': blue_side_champs,
    'Red Side Champions': red_side_champs
    })

    return df

def getDataSet():
    
    challQ = getChallengerQ()
    if challQ is None:
        print("None")
        return
    challSummonerIds = [entry['summonerId'] for entry in challQ['entries']]
    print(len(challSummonerIds))

    puuids = convertSummonerIdsToPuuids(challSummonerIds)
    print(len(puuids))

    matchIds = getMatchIds(puuids)
    print(matchIds)

    # id = matchIds.pop()
    print(len(matchIds))
    dataset = getMatchData(matchIds)

    dataset.to_csv('output.csv', index=False)

    return dataset

    
getDataSet()