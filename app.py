# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd





external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
match_data_18 = pd.read_csv('export_data/data_6_18.csv')
match_data_17 = pd.read_csv('export_data/data_6_17.csv')
match_data_15 = pd.read_csv('export_data/data_6_15.csv')
match_data_total = pd.concat([match_data_15, match_data_17, match_data_18])
subset = ['puuid', 'kills', 'deaths','assists', 'totalDamageDealt', 'totalDamageTaken', 'totalHeal', 'item0', 'item1', 'item2', 'item3', 'item4', 'item5', 'item6']
match_data_total_deduped = match_data_total.drop_duplicates(subset, keep = 'first')
test = match_data_total_deduped.groupby(['teamPosition', 'championName'])['matchId'].agg('count').reset_index()
test.rename(columns = {'matchId':'matchCount'}, inplace = True)
test_sorted = test.sort_values(['teamPosition', 'matchCount'], ascending = [True, False])
test_filtered = test_sorted.loc[test_sorted['teamPosition'] != 'AFK']
test_filtered
top3_bottom = ['Ezreal', 'Kaisa', 'Tristana']
top3_jungle = ['Kindred', 'Kayn', 'Rumble']
top3_mid = ['Sylas', 'LeeSin', 'Lucian']
top3_top = ['LeeSin', 'Jayce', 'Gwen']
top3_supp = ['Thresh', 'Nautilus', 'Karma']

bot_mask = test_sorted['teamPosition'] == 'BOTTOM'
jung_mask = test_sorted['teamPosition'] == 'JUNGLE'
mid_mask = test_sorted['teamPosition'] == 'MIDDLE'
top_mask = test_sorted['teamPosition'] == 'TOP'
supp_mask = test_sorted['teamPosition'] == 'UTILITY'

top3_all_lanes = test.loc[
    (bot_mask & test['championName'].isin(top3_bottom)) |
    (jung_mask & test['championName'].isin(top3_jungle)) |
    (mid_mask & test['championName'].isin(top3_mid)) |
    (top_mask & test['championName'].isin(top3_top)) |
    (supp_mask & test['championName'].isin(top3_supp))
]
top3_all_lanes_sorted = top3_all_lanes.sort_values(['teamPosition', 'matchCount'], ascending = [True, False])
top3_all_lanes_sorted.loc[top3_all_lanes_sorted['teamPosition'] == 'UTILITY', 'teamPosition'] = 'SUPPORT'
top3_all_lanes_sorted


fig = px.bar(top3_all_lanes_sorted, x = 'teamPosition', y = 'matchCount', color = 'championName', text = 'matchCount',
             color_discrete_map = {
                'Ezreal': '#5F9EA0',
                'Tristana': '#FFA07A',
                'Kaisa': '#4B0082',
                'Rumble': '#CD853F',
                'Kindred': '#708090',
                'Kayn': '#4682B4',
                'Lucian': '#DCDCDC',
                'LeeSin': '#A0522D',
                'Sylas': '#191970',
                'Gwen': '#40E0D0',
                'Jayce': '#D2B48C',
                'Nautilus': '#2E8B57',
                'Thresh': '#556B2F',
                'Karma': '#FFB6C1'
            },

             labels = {'teamPosition': 'Position', 'matchCount': '# of Games Played', 'championName': 'Champion'}, title = 'Top 3 Champions Played by Position')
fig.update_layout(
    plot_bgcolor = 'rgb(0,0,0,0)',
    paper_bgcolor = 'rgb(0,0,0,0)',
    width = 1200,
    height = 800,
    title_x = 0.5,
    legend = dict(bgcolor = 'white', yanchor = 'top', y = 0.88, xanchor = 'right', x = 1.10),
    legend_title = dict(font = dict(size = 14)),
)
fig.update_xaxes(categoryorder = 'total ascending')

fig.layout.legend.tracegroupgap = 14

fig.update_traces(texttemplate = '%{text} Games', textposition = 'inside', insidetextanchor = 'middle')

app.layout = html.Div(children=[
    html.H1(children='League of Legends Dashboard WIP'),

    html.Div(children='''
        Champion Analysis
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)