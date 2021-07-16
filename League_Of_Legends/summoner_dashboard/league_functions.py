import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px
import pandas as pd
import numpy as np
import requests
import regex as re
import json
import pprint
import time

from pandas.io.pytables import Table
from league_functions import *





REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Charset': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://developer.riotgames.com',
    'X-Riot-Token': ''
    }


RIOT_API = 'RGAPI-9117d7f3-c0d0-415a-be8b-6105e2038f6e'

def create_champion_mapping_dict(file_name):
    champion_key_dict = {}
    with open(f'League_Of_Legends/json_files/{file_name}', encoding = 'utf-8') as f:
        champion_json = json.load(f)
        for champion, info in champion_json['data'].items():
            champion_name = champion
            for c_key, c_value in info.items():
                if c_key == 'key':
                    champion_key_dict[champion_name] = int(c_value)
    return champion_key_dict

def create_item_mapping_dict(file_name):
    item_key_dict = {}
    with open(f'League_Of_Legends/json_files/{file_name}', encoding = 'utf-8') as f:
        item_data = json.load(f)
        for item, info in item_data['data'].items():
            item_id = item
            for i_key, i_value in info.items():
                if i_key == 'name':
                    item_key_dict[int(item_id)] = i_value
    return item_key_dict

def create_queue_mapping_dict(file_name):
    queue_info_dict = {}
    with open(f'League_Of_Legends/json_files/{file_name}', encoding = 'utf-8') as f:
        queue_data = json.load(f)
        for queue in queue_data:
            queue_key = queue['queueId']
            queue_name = queue['description']
            queue_notes = str(queue['notes'])
            if 'deprecated' not in queue_notes.lower():
                queue_info_dict[queue_key] = str(queue_name).upper()

    queue_info_dict_reverse = {str(v).upper(): k for (k,v) in queue_info_dict.items()}
    return queue_info_dict, queue_info_dict_reverse


def create_summoner_spell_mapping_dict(file_name):
    ss_info_dict = {}
    with open(f'League_Of_Legends/json_files/{file_name}', encoding = 'utf-8') as f:
        ss_data = json.load(f)
        for s_spell, info in ss_data['data'].items():
            for key in info:
                ss_key = info['key']
                ss_name = info['name']
                ss_description = info['description']
                ss_info_dict[ss_name] = (ss_key, ss_description)
    return ss_info_dict


def create_season_mapping_dict(file_name):
    season_info_dict = {}
    with open(f'League_Of_Legends/json_files/{file_name}', encoding = "utf-8") as f:
        season_data = json.load(f)
        for season in season_data:
            season_info_dict[season['id']] = season['season']
    return season_info_dict
    

champion_key_dict = create_champion_mapping_dict('champion.json')
item_key_dict = create_item_mapping_dict('item.json')
queue_key_dict, queue_key_dict_reverse = create_queue_mapping_dict('queue.json')
ss_key_dict = create_summoner_spell_mapping_dict('summoner.json')    
season_key_dict = create_season_mapping_dict('season.json')




def get_puu_id(summoner_name, riot_api_key = RIOT_API, request_headers = REQUEST_HEADERS, access = True):
    summoner_name_updated = summoner_name.replace(' ', '%20')
    url = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/'
    account_url = url + summoner_name_updated
    riot_headers = request_headers
    riot_headers["X-Riot-Token"] = riot_api_key
    while access:
        req = requests.get(account_url, headers = riot_headers)
        if req.status_code == 200:
            account_info = json.loads(req.content.decode("utf-8"))
            puu_id = account_info['puuid']
            access = False

        elif req.status_code == 404:
            puu_id = None
            access = False

        else:
            print('Waiting for 10 seconds to refresh restriction request for getting PUU ID')
            time.sleep(10)
    return  puu_id

def get_match_id(puu_id, start, count, riot_api_key = RIOT_API, request_headers = REQUEST_HEADERS, access = True):
    match_id = None
    match_history_url = f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puu_id}/ids?start={start}&count={count}'
    riot_headers = request_headers
    riot_headers["X-Riot-Token"] = riot_api_key

    while access:
        req = requests.get(match_history_url, headers = riot_headers)
        if req.status_code == 200:
            match_id_listed = json.loads(req.content.decode("utf-8"))
            match_id = ''.join(match_id_listed)
            access = False
            
        else:
            print('Waiting for 10 seconds to refresh restriction request for getting Match ID')
            time.sleep(10)
            
    return match_id


def get_match_details(match_id, riot_api_key = RIOT_API, request_headers = REQUEST_HEADERS, access = True):
    match_url = 'https://americas.api.riotgames.com/lol/match/v5/matches/' + str(match_id)
    riot_headers = request_headers
    riot_headers["X-Riot-Token"] = riot_api_key

    while access:
        req = requests.get(match_url, headers = riot_headers)
        if req.status_code == 200:
            match_details = json.loads(req.content.decode("utf-8"))
            access = False

        elif req.status_code == 404:
            match_details = None
            access = False
            
        else:
            print(req.status_code)
            print('Waiting for 10 seconds to refresh restriction request for getting Match Details')
            time.sleep(10)

    return match_details

def clean_and_reduce_match_data(match_details):
    match_cleaned_dict = {}
    
    match_id = None
    match_timestamp = None
    queue_id = None
    participant_details = None
    
    
    for key, value in match_details['info'].items():
        if key == 'gameId':
            match_id = value
            
        if key == 'queueId':
            queue_id = value
            
        if key == 'gameStartTimestamp':
            match_timestamp = value
            
        if key == 'participants':
            participant_details = value
    
    if queue_id == 420:
        match_cleaned_dict[(match_id, queue_id, match_timestamp)] = participant_details
                
        return match_cleaned_dict
    
    else:
        return None

def filter_match_data_by_puuid(match_cleaned_dict, puu_id):
    for match_id, match_details in match_cleaned_dict.items():
        for participant_dict in match_details:
            if participant_dict['puuid'] == puu_id:
                return {str(match_id[0]) + '_' + str(match_id[1]) + '_' + str(match_id[2]): participant_dict}

def remove_perks_attribute(match):
    for key, info in match.items():
        for key in list(info.keys()):
            if key == 'perks':
                del info[key]

    return match


def make_match_df(match):
    match_df = pd.DataFrame.from_dict(match, orient = 'index')
    return match_df

def get_match_detail_by_summoner_name(summoner_name, beg, end, riot_api = RIOT_API, request_headers = REQUEST_HEADERS):
    
    puu_id = get_puu_id(summoner_name, riot_api, request_headers)
    match_detail_df = None
    
    if puu_id != None:
        match_id = get_match_id(puu_id, start = beg, count = end)
        match_detail = get_match_details(match_id)
        if match_detail != None:
            match_cleaned = clean_and_reduce_match_data(match_detail)
            if match_cleaned != None:
                match_cleaned_filtered = filter_match_data_by_puuid(match_cleaned, puu_id)

                match_final = remove_perks_attribute(match_cleaned_filtered)

                match_detail_df = make_match_df(match_final)
                    
                return match_detail_df
        
            else:
                print(f'MATCH ID {match_id} IS NOT A RANKED SOLO GAME')
                return 'NO MATCH ID'
    
        else:
            print(f'NO MATCH DETAIL FOUND FOR MATCH ID: {match_id}')   
            return 'NO MATCH DETAIL'
    else:
        print(f'NO PUU ID FOUND FOR SUMMONER: {summoner_name}')
        return 'NO PUU ID'

def clean_columns(data):
    data = data.reset_index()

    cleaned_cols = list(data.columns.values)[1:]

    data[['matchId', 'queueId','matchStartTimeStamp']] = data['index'].str.split('_', expand = True)

    cleaned_cols = ['matchId', 'queueId','matchStartTimeStamp'] + cleaned_cols
    data = data[cleaned_cols]

    return data

def mapping_data_values(data, mapping_key):
    if mapping_key == 'Q':
        data['queueId'] = data['queueId'].astype(int)
        data['queueId'] = data['queueId'].map(queue_key_dict)

    if mapping_key == 'I':
        item_columns = ["item0", "item1", "item2", "item3", "item4", "item5", "item6"]
        for col in item_columns:
            data[col] = data[col].map(item_key_dict)

    if mapping_key == 'S':
        summoner_columns = ['summoner1Id', 'summoner2Id']
        for col in summoner_columns:
            data[col] = data[col].map(ss_key_dict)
    
    if mapping_key == 'T':
        team_color = data['teamId'].map({100: 'Blue', 200: 'Red'})
        data.insert(1, 'teamColor', team_color)
    
    return data

def initial_cleanup(data):
    data = clean_columns(data)
    
    for letter in ['Q', 'I', 'S', 'T']:
        data = mapping_data_values(data, letter)        

    return data

def get_clean_match_data_by_summoner(summoner_name, beg, end):

    df = get_match_detail_by_summoner_name(summoner_name, beg, end)
    
    if isinstance(df, pd.DataFrame):
        df = initial_cleanup(df)

    return df


def get_summoner_match_clean_df(summoner_name, beg, end, num_games):

    solo_game_count = 0
    df_listed = []

    print(f'STARTED PROCESSING FOR SUMMONER: {summoner_name}')
    print('')

    while solo_game_count < num_games:
        print(f'ROW {beg} HAS BEEN PROCESSED')
        df = get_clean_match_data_by_summoner(summoner_name, beg, end)
        beg += 1

        if isinstance(df, pd.DataFrame):
            solo_game_count += df.shape[0]
            print(f'SOLO GAME ROW COUNT: {solo_game_count}')
            print('')
            df_listed.append(df)
        
        elif df == 'NO MATCH ID':
            continue
        
        elif df == 'NO MATCH DETAIL':
            continue
        else:
            print('MOVING ON TO NEXT SUMMONER')
            print('')
            break
        
    if df_listed != []:
        final = pd.concat(df_listed)
        return final
    else:
        return None



def final_cleanup(data):
    data['matchStartTimeStamp'] = data['matchStartTimeStamp'].astype('int64')
    data['matchStartTimeStamp'] = pd.to_datetime(data['matchStartTimeStamp'], unit='ms')
    
    item_cols = ['item0', 'item1', 'item2', 'item3', 'item4', 'item5', 'item6']
    other_cols = ['inhibitorsLost', 'nexusLost', 'turretsLost',  'damageDealtToBuildings', 'inhibitorTakedowns', 'nexusTakedowns', 'turretTakedowns']
    null_cols = ['riotIdName', 'riotIdTagline', 'summoner1Id', 'summoner2Id', 'unrealKills', 'sightWardsBoughtInGame']
    useless_cols = ['role', 'lane', 'individualPosition']
    
    data.loc[data['teamPosition'] == 'UTILITY', 'teamPosition'] = 'SUPPORT'
    data.loc[data['individualPosition'] == 'UTILITY', 'individualPosition'] = 'SUPPORT'
    data.loc[data['championName'] == 'MonkeyKing', 'championName'] = 'Wukong'
   

    data.drop_duplicates(inplace = True)

    data.loc[: , item_cols] = data[item_cols].fillna(value = 'None')
    data.loc[: , other_cols] = data[other_cols].fillna(value = 0)
    
    data.drop(columns = null_cols, inplace = True)
    data.drop(columns = useless_cols, inplace = True)
    
    
    return data