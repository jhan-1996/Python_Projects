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


# data
#################################################################################################################################################################################
# dashboard to see a summoner's profile based off the most recent x ranked games

summoner_name = input('Enter Summoner Name: ')
num_games = int(input('Enter # of Games: '))

df = get_summoner_match_clean_df(summoner_name, beg = 0, end = 1, num_games = num_games)
df = final_cleanup(df)
print(df)
# figure
#################################################################################################################################################################################

# fig1 = px.bar(average_kda_df_long, x = 'Champion', y = 'stat_count', color = 'stat_type', barmode = 'group', text = 'stat_count',
#              labels = {'stat_count': '', 'stat_type': 'KDA'}, title = 'KDA for Top 10 Played Champions')

# for data in fig1.data:
#     data["width"] = 0.30

# fig1.update_layout(
#     plot_bgcolor = 'rgb(0,0,0,0)',
#     paper_bgcolor = 'rgb(0,0,0,0)',
#     width = 1100,
#     height = 800,
#     title_x = 0.5,
#     legend = dict(bgcolor = 'white', yanchor = 'top', y = 0.60, xanchor = 'right', x = 1.20),
#     legend_title = dict(font = dict(size = 12)),
# )
# fig1.update_xaxes(categoryorder = 'total ascending')
# fig1.layout.legend.tracegroupgap = 24

# fig2 = px.bar(top3_all_lanes_sorted, x = 'teamPosition', y = 'matchCount', color = 'championName', text = 'matchCount',
#              color_discrete_map = {
#                 'Ezreal': '#5F9EA0',
#                 'Tristana': '#FFA07A',
#                 'Kaisa': '#4B0082',
#                 'Rumble': '#CD853F',
#                 'Kindred': '#708090',
#                 'Kayn': '#4682B4',
#                 'Lucian': '#DCDCDC',
#                 'LeeSin': '#A0522D',
#                 'Sylas': '#191970',
#                 'Gwen': '#40E0D0',
#                 'Jayce': '#D2B48C',
#                 'Nautilus': '#2E8B57',
#                 'Thresh': '#556B2F',
#                 'Karma': '#FFB6C1'
#             },

#              labels = {'teamPosition': 'Position', 'matchCount': '# of Games Played', 'championName': 'Champion'}, title = 'Top 3 Champions Played by Position')
# fig2.update_layout(
#     plot_bgcolor = 'rgb(0,0,0,0)',
#     paper_bgcolor = 'rgb(0,0,0,0)',
#     width = 700,
#     height = 800,
#     title_x = 0.5,
#     legend = dict(bgcolor = 'white', yanchor = 'top', y = 0.96, xanchor = 'right', x = 1.20),
#     legend_title = dict(font = dict(size = 12)),
# )
# fig2.update_xaxes(categoryorder = 'total ascending')

# fig2.layout.legend.tracegroupgap = 24

# fig2.update_traces(texttemplate = '%{text} Games', textposition = 'inside', insidetextanchor = 'middle')

# # app layout
# #################################################################################################################################################################################


# def generate_table(dataframe, max_rows=15):
#     return html.Table([
#         html.Thead(
#             html.Tr([html.Th(col) for col in dataframe.columns])
#         ),
#         html.Tbody([
#             html.Tr([
#                 html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
#             ]) for i in range(min(len(dataframe), max_rows))
#         ])
#     ])



# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

# app.layout = html.Div(
#     children = [
#         html.H1(
#             children ='HELLO KYUNGS', 
#             style = {'textAlign': 'center'}
#             ),

#         html.Div(
#             children = [
#                 dcc.Graph(id = 'kda_top10', figure = fig1, style = {'display': 'inline-block', 'margin-left': '10px'}),
#                 dcc.Graph(id = 'top3_by_lane', figure = fig2, style = {'display': 'inline-block', 'margin-left': '120px'})
#             ]),

#         html.Div([
#                 html.Div([dash_table.DataTable(id = '1', 
#                     columns=[{"name": i, "id": i} for i in average_kda_df_top_10_gamecount_cleaned.columns],
#                     data = average_kda_df_top_10_gamecount_cleaned.to_dict('records'))], style = {'display': 'inline-block', 'margin-left': '95px'}),
#                 html.Div([dash_table.DataTable(id = '2', 
#                     columns=[{"name": i, "id": i} for i in top3_all_lanes_sorted.columns],
#                     data = top3_all_lanes_sorted.to_dict('records'))], style = {'display': 'inline-block', 'margin-left': '695px'}),
#                 ]),
# ])

# if __name__ == '__main__':
#     app.run_server(debug=True)
