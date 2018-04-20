import requests
import json
from bs4 import BeautifulSoup
import sqlite3
import plotly.plotly as py
import plotly.graph_objs as go

CACHE_FNAME = 'cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_DICTION = {}


def get_unique_key(url):
  return url

def make_request_using_cache(url):
    unique_ident = get_unique_key(url)

    if unique_ident in CACHE_DICTION:
        return CACHE_DICTION[unique_ident]

    else:
        resp = requests.get(url)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICTION[unique_ident]


class Player:
    def __init__(self, name = None, team = None, position = None, year = None):
        self.name = name
        self.position = position
        if self.position == "Umpire" or self.position == "Executive":
            self.team = "Unaffiliated"
        else:
            self.team = team
        self.year_inducted = year

    def __str__(self):
        return "{}, {} for the {} (Inducted in {})".format(self.name, self.position, self.team, self.year_inducted)

def make_players_list():
    final_list = []
    counter = 0
    while counter <= 13:
        page_text = make_request_using_cache('https://baseballhall.org/explorer?page=' + str(counter))
        page_soup = BeautifulSoup(page_text, 'html.parser')
        players_list = page_soup.find_all(class_='famer-data')
        for plyr in players_list:
            try:
                name_data = plyr.find(class_='name').text
            except:
                name_data = "None"
            try:
                year_data = plyr.find(class_='year').text
            except:
                year_data = "None"
            try:
                team_data = plyr.find(class_='primary-team').text[14:]
            except:
                team_data = "MLB"
            try:
                position_data = plyr.find(class_='position-field').text
            except:
                position_data = "None"
            add_player = Player(name_data, team_data, position_data, year_data)
            final_list.append(add_player)
        counter += 1
    return final_list

def get_famers_per_team():
    final_list = []

    conn = sqlite3.connect('baseball.db')
    cur = conn.cursor()
    cur.execute('SELECT Teams.Team, COUNT(*) FROM Teams JOIN Players ON Teams.Id = Players.TeamId GROUP BY Teams.Team')

    sub_list1 = []
    sub_list2 = []
    for row in cur:
        sub_list1.append(row[0])
        sub_list2.append(row[1])

    final_list.append(sub_list1)
    final_list.append(sub_list2)
    return final_list

def make_famers_per_team_graph():
    lst = get_famers_per_team()
    data = [go.Bar(x = lst[0], y = lst[1])]
    layout = go.Layout(
    xaxis=dict(
        type='Category',
    ))
    py.plot(data, filename='basic-bar')

def get_famers_per_position():
    final_list = []

    conn = sqlite3.connect('baseball.db')
    cur = conn.cursor()
    cur.execute('SELECT Players.Position, COUNT(*) FROM Teams JOIN Players ON Teams.Id = Players.TeamId GROUP BY Players.Position')
    sub_list1 = []
    sub_list2 = []
    for row in cur:
        sub_list1.append(row[0])
        sub_list2.append(row[1])

    final_list.append(sub_list1)
    final_list.append(sub_list2)
    return final_list

def make_famers_per_position_graph():
    lst = get_famers_per_position()
    labels = lst[0]
    values = lst[1]
    trace = go.Pie(labels=labels, values=values)
    py.plot([trace], filename='basic_pie_chart')


def get_famers_per_year():
    final_list = []

    conn = sqlite3.connect('baseball.db')
    cur = conn.cursor()
    cur.execute('SELECT Players.YearInducted, COUNT(*) FROM Teams JOIN Players ON Teams.Id = Players.TeamId GROUP BY Players.YearInducted ORDER BY Players.YearInducted ASC')
    sub_list1 = []
    sub_list2 = []
    for row in cur:
        sub_list1.append(int(row[0]))
        sub_list2.append(row[1])

    final_list.append(sub_list1)
    final_list.append(sub_list2)
    return final_list

def make_famers_per_year_graph():
    lst = get_famers_per_year()
    trace = go.Scatter(x = lst[0], y = lst[1])
    data = [trace]
    py.plot(data, filename='basic-line')

def make_famers_per_team_pie_graph():
    lst = get_famers_per_team()
    labels = lst[0]
    values = lst[1]
    trace = go.Pie(labels=labels, values=values)
    py.plot([trace], filename='basic_pie_chart')


conn = sqlite3.connect('baseball.db')
cur = conn.cursor()

statement = '''
CREATE TABLE 'Players' (
    'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'FirstName' TEXT NOT NULL,
    'LastName' TEXT NOT NULL,
    'Position' TEXT NOT NULL,
    'YearInducted' INTEGER NOT NULL,
    'TeamId' INTEGER NOT NULL
    );
    '''
cur.execute(statement)

statement = '''
CREATE TABLE 'Teams' (
    'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'Team' TEXT NOT NULL
    );
    '''
cur.execute(statement)

plyr_lst = make_players_list()

team_list = []
for x in plyr_lst:
    if x.team not in team_list:
        team_list.append(x.team)

for x in team_list:
    insertion = (None, x)
    statement = 'INSERT INTO "Teams" '
    statement += 'VALUES (?, ?)'
    cur.execute(statement, insertion)

cur.execute('SELECT Id, Team FROM Teams')
team_dict = {}
for row in cur:
    if row[1] not in team_dict.keys():
        team_dict[row[1]] = row[0]

for x in plyr_lst:
    split_name = x.name.split(',')
    first_name = split_name[1]
    last_name = split_name[0]
    insertion = (None, first_name, last_name, x.position, x.year_inducted, team_dict[x.team])
    statement = 'INSERT INTO "Players" '
    statement += 'VALUES (?, ?, ?, ?, ?, ?)'
    cur.execute(statement, insertion)

conn.commit()
conn.close()

if __name__=="__main__":
    running = True
    while running == True:
          response = input('Enter players, teams, graphs or exit: ')
          if response == "exit":
              running = False
              print("bye")
              break
          elif response == "players":
              conn = sqlite3.connect('baseball.db')
              cur = conn.cursor()

              cur.execute('SELECT Id, Players.FirstName, Players.LastName FROM Players')
              for row in cur:
                  edited_row = "{} {} {}".format(row[0],row[1],row[2])
                  print(edited_row)

              response = input("What player number would you like more info on? ")
              try:
                  statement = 'SELECT FirstName, LastName, Position, Team, YearInducted FROM Players  JOIN Teams ON Players.TeamId = Teams.Id WHERE Players.Id = ?'
                  params = (response,)
                  cur.execute(statement,params)
                  for row in cur:
                      edited_row = "{} {}, {} for the {} (Inducted in {})".format(row[0],row[1],row[2],row[3],row[4])
                      print(edited_row)
              except:
                  print("Not a valid player number")
          elif response == "teams":
              conn = sqlite3.connect('baseball.db')
              cur = conn.cursor()

              cur.execute('SELECT Id, Team FROM Teams ORDER BY Team')
              for row in cur:
                  edited_row = "{} {}".format(row[0],row[1])
                  print(edited_row)

              response = input("What team number would you like to see a list of Hall of Famers for? ")

              try:
                  statement = 'SELECT Players.Id, FirstName, LastName FROM Players  JOIN Teams ON Players.TeamId = Teams.Id WHERE Teams.Id = ?'
                  params = (response,)
                  cur.execute(statement,params)
                  for row in cur:
                      edited_row = "{} {} {}".format(row[0],row[1],row[2])
                      print(edited_row)
              except:
                  "Not a valid team number"

              response2 = input("What player number would you like more info on? ")
              try:
                  statement = 'SELECT FirstName, LastName, Position, Team, YearInducted FROM Players  JOIN Teams ON Players.TeamId = Teams.Id WHERE Players.Id = ?'
                  params = (response2,)
                  cur.execute(statement,params)
                  for row in cur:
                      edited_row = "{} {}, {} for the {} (Inducted in {})".format(row[0],row[1],row[2],row[3],row[4])
                      print(edited_row)
              except:
                  "Not a valid player number"
          elif response == "graphs":
              print("Graph Options:")
              print("1 - Bar Graph of Hall of Famers on Each Team")
              print("2 - Pie Graph of Hall Famers at Each Position")
              print("3 - Line Graph of Number of Hall Famers Inducted Each Year Over Time")
              print("4 - Pie Graph of Number of Hall Famers on Each Team")
              response = input("What graph number would you like to view? ")
              if response == "1":
                  make_famers_per_team_graph()
              if response == "2":
                  make_famers_per_position_graph()
              if response == "3":
                  make_famers_per_year_graph()
              if response == "4":
                  make_famers_per_team_pie_graph()
          else:
            print("Not valid input")
