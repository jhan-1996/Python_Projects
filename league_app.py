import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from pandas.io.pytables import Table
import plotly.express as px
import pandas as pd
import numpy as np



# data

def generate_table(dataframe, max_rows=15):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

df = pd.read_csv('export_data/data_combined.csv')
average_kda = df.loc[:, ['championName', 'kills', 'deaths', 'assists', 'matchId']].groupby('championName').agg({
    'kills': 'mean', 'deaths': 'mean', 'assists': 'mean', 'matchId': 'count'
})
average_kda.rename(columns = {'matchId': 'game_count'}, inplace = True)
average_kda_df = average_kda.reset_index()
average_kda_df_top_10_gamecount = average_kda_df.sort_values(by = 'game_count', ascending = False).iloc[:10, :]

average_kda_df_top_10_gamecount_cleaned = average_kda_df_top_10_gamecount.rename(
    columns = {'championName': 'Champion', 'kills': 'Average Kills', 'deaths': 'Average Deaths', 'assists': 'Average Assists', 'game_count': '# of Games'}
)
average_kda_df_top_10_gamecount_cleaned['Average Kills'] = round(average_kda_df_top_10_gamecount_cleaned['Average Kills'], 1)
average_kda_df_top_10_gamecount_cleaned['Average Deaths'] = round(average_kda_df_top_10_gamecount_cleaned['Average Deaths'], 1)
average_kda_df_top_10_gamecount_cleaned['Average Assists'] = round(average_kda_df_top_10_gamecount_cleaned['Average Assists'], 1)

average_kda_df_top_10_nogamecount =  average_kda_df_top_10_gamecount_cleaned.drop(columns = '# of Games')
average_kda_df_long = pd.melt(average_kda_df_top_10_nogamecount, id_vars = ['Champion'], var_name = 'stat_type', value_name = 'stat_count')


test = df.groupby(['teamPosition', 'championName'])['matchId'].agg('count').reset_index()
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
supp_mask = test_sorted['teamPosition'] == 'SUPPORT'

top3_all_lanes = test.loc[
    (bot_mask & test['championName'].isin(top3_bottom)) |
    (jung_mask & test['championName'].isin(top3_jungle)) |
    (mid_mask & test['championName'].isin(top3_mid)) |
    (top_mask & test['championName'].isin(top3_top)) |
    (supp_mask & test['championName'].isin(top3_supp))
]
top3_all_lanes_sorted = top3_all_lanes.sort_values(['teamPosition', 'matchCount'], ascending = [True, False])


# figure
fig1 = px.bar(average_kda_df_long, x = 'Champion', y = 'stat_count', color = 'stat_type', barmode = 'group', text = 'stat_count',
             labels = {'stat_count': '', 'stat_type': 'KDA'}, title = 'KDA for Top 10 Played Champions')

for data in fig1.data:
    data["width"] = 0.30

fig1.update_layout(
    plot_bgcolor = 'rgb(0,0,0,0)',
    paper_bgcolor = 'rgb(0,0,0,0)',
    width = 1000,
    height = 600,
    title_x = 0.5,
    legend = dict(bgcolor = 'white', yanchor = 'top', y = 0.96, xanchor = 'right', x = 1.20),
    legend_title = dict(font = dict(size = 12)),
)
fig1.update_xaxes(categoryorder = 'total ascending')

fig2 = px.bar(top3_all_lanes_sorted, x = 'teamPosition', y = 'matchCount', color = 'championName', text = 'matchCount',
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
fig2.update_layout(
    plot_bgcolor = 'rgb(0,0,0,0)',
    paper_bgcolor = 'rgb(0,0,0,0)',
    width = 700,
    height = 800,
    title_x = 0.5,
    legend = dict(bgcolor = 'white', yanchor = 'top', y = 0.96, xanchor = 'right', x = 1.20),
    legend_title = dict(font = dict(size = 12)),
)
fig2.update_xaxes(categoryorder = 'total ascending')

fig2.layout.legend.tracegroupgap = 8

fig2.update_traces(texttemplate = '%{text} Games', textposition = 'inside', insidetextanchor = 'middle')

# app layout


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

app.layout = html.Div(
    children = [
        html.H1(
            children ='HELLO KYUNGS', 
            style = {'textAlign': 'center'}
            ),

        html.Div(
            children = [
                dcc.Graph(id = 'kda_top10', figure = fig1, style = {'display': 'inline-block', 'margin-left': '10px'}),
                dcc.Graph(id = 'top3_by_lane', figure = fig2, style = {'display': 'inline-block', 'margin-left': '120px'})
            ]),

        html.Div([
                html.Div([dash_table.DataTable(id = '1', 
                    columns=[{"name": i, "id": i} for i in average_kda_df_top_10_gamecount_cleaned.columns],
                    data = average_kda_df_top_10_gamecount_cleaned.to_dict('records'))], style = {'display': 'inline-block', 'margin-left': '95px'}),
                html.Div([dash_table.DataTable(id = '2', 
                    columns=[{"name": i, "id": i} for i in top3_all_lanes_sorted.columns],
                    data = top3_all_lanes_sorted.to_dict('records'))], style = {'display': 'inline-block', 'margin-left': '695px'}),
                ]),
])

if __name__ == '__main__':
    app.run_server(debug=True)
