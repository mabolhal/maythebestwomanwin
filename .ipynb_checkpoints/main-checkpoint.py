import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_table
import praw

import pandas as pd
import requests
from bs4 import BeautifulSoup
import joblib
import unicodedata
import json

# from rpdr_main import retrieve_seasons


external_stylesheets = [dbc.themes.BOOTSTRAP]

# ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,prevent_initial_callbacks=True)

with open('reddit_credentials.json') as credentials:
    data = json.load(credentials)
    client_id = data.get("client_id")
    client_secret = data.get("client_secret")
    user_agent = data.get("user_agent")
    redirect_uri= data.get("redirect_uri")

reddit = praw.Reddit(client_id=client_id, client_secret=client_secret,user_agent=user_agent)

loaded_model = joblib.load('classification_model.pkl')

def create_df_reddit_comments(episode_id):
    comments_dict = {
        'comment_id': [],
        'comment' : []
        }
    submission = reddit.submission(id=episode_id)
    submission.comments.replace_more(limit=None)
    for h in submission.comments:
        comments_dict['comment_id'].append(h.id)
        comments_dict['comment'].append(h.body)
    result = pd.DataFrame(comments_dict)
    return result


def queens_mentioned(df, queens):
    print(queens)
    result = []
    for comment in df.comment:
        row_result = []
        for queen in queens:
            if string_compare(queen, comment):
                row_result.append(queen)
        result.append(row_result)
    return result 


def string_compare(a, b):
    b = b.lower()
    a = a.lower()
    a = a.split(' ')[0]
    if (a in b) or (a.lower() in b) or (remove_accents(a) in remove_accents(b)) or (a+"'s" in b) or (a+"s"in b):
        return True
    else:
        return False
    

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])
        
    
def display_info(episode_id, queens):
    df = create_df_reddit_comments(episode_id)
    df["queens"] = queens_mentioned(df, queens)
    df["model_predicted"] = loaded_model.predict(df["comment"])
    result = html.Div(
        [
            dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)
        ]
    )
    return result


def retrieve_episode_id(season_number):
    episodes = []
    rpdr = reddit.subreddit('rupaulsdragrace')
    season_number = str(season_number) if season_number > 9 else '0'+str(season_number)
    for n in range(1, 15):
        episode_search_string = str(n) if n > 9 else '0'+str(n)
        for i in rpdr.search(f'UNTUCKED S{season_number}E'+episode_search_string, limit=1):
            episodes.append([i.id, episode_search_string])
    return episodes


def retrieve_seasons():
    url = "https://en.wikipedia.org/wiki/RuPaul%27s_Drag_Race"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    result = soup.find_all('td')[10].text
    return int(result) 


def retrieve_queens(season):
    url = f"https://rupaulsdragrace.fandom.com/wiki/Category:Season_{season}_Queens"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    result = []
    for queen_name in soup.find_all("div", class_="lightbox-caption"):
        result.append(queen_name.text)
    return result


number_of_seasons = retrieve_seasons()

app.layout = html.Div(children=[
    html.H1(id='header', children='RuPaul\'s Drag Race Sentiment Analysis'),
    dcc.Markdown("""
    This app takes a look at what people are saying about the queens on RPDR. Analysis of the queens' comments... I'll write this part later.
    """),
    html.H5(children='Select a Season:'),
    dcc.Dropdown(
        id='select-season',
        options=[
            {'label': f'Season {i}', 'value': i} for i in range(7, number_of_seasons+1)
        ]
    ),
    dbc.Button(id="submit", children="Submit", n_clicks=0, color="primary", className="mr-1"),
    html.Div(id="result_container")
])



@app.callback(
    Output(component_id='result_container', component_property='children'),
    Input(component_id='submit', component_property='n_clicks'),
    State('select-season', 'value')
)
def update_output_div(n, season_number):
    if n:
        episode_numbers = retrieve_episode_id(season_number)
#         print(season_number)
        contestants_df = pd.DataFrame(retrieve_queens(season_number))
        contestants_df.columns = ["Queens"]
        result = [
            html.H5("Contestants: "),
            html.Div([
                dash_table.DataTable(
                    id='table',
                    columns=[{"name": i, "id": i} 
                             for i in contestants_df.columns],
                    data=contestants_df.to_dict('records'),
                    style_cell=dict(textAlign='center'),
                )
            ]),
            html.H5("Untucked Stats: "),
            html.P("Untucked Episodes"),
            html.Div([
                dbc.Tabs([dbc.Tab(label=i[1], children=display_info(i[0], contestants_df["Queens"])) for i in episode_numbers])
            ])
        ]
        return result




if __name__ == '__main__':
    app.run_server(debug=True)