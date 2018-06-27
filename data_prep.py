import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import html5lib

all_active_players = []

# according pfr the last player Sebstian Janikowski is the earlest
# active player drafted (2000 draft)
# NOTE undrafted players are not included in this, so guys like Adam Vinatieri
# are not included
for year in range(2000,2016):
    # get the html and extract the data based off the proper CSS selector
    url = "http://www.pro-football-reference.com/years/{}/draft.htm".format(year)
    html = urlopen(url)
    soup = BeautifulSoup(html, "html5lib")
    # active drafted players are bolded in the draft table on pfr
    player_html = soup.select("#drafts strong a")
    # get the link for each
    player_links = [player["href"] for player in player_html]
    # add these links to the large list active player lists
    all_active_players.extend(player_links)

# Extract the player ids for each using regex
active_player_ids = [re.search(r"/.*/.*/(.*)\.", player).group(1) for player
                     in all_active_players]

#print (active_player_ids[:5]) # just check things out, need to drop charles woodson as he's retired

draft_df = pd.read_csv("pfr_nfl_draft_data_CLEAN.csv")

# convert the data to proper numeric types
draft_df = draft_df.convert_objects(convert_numeric=True)

# Get the column names for the numeric columns
num_cols = draft_df.columns[draft_df.dtypes != object]

# Replace all NaNs with 0
draft_df.loc[:, num_cols] = draft_df.loc[:, num_cols].fillna(0)

#print (draft_df.head())

# keep only players before the 2016 draft
draft_df = draft_df.loc[draft_df.Draft_Yr < 2016]

#print (draft_df.tail())

# create a seriess indicating whether a player is active
active = draft_df.Player_ID.isin(active_player_ids)

# Now create a column indicating that a player's career is officially over
# via ~ and convert it to 1s and 0s
draft_df["Retired"] = (~active).astype(int)

#print(draft_df.info())


#print (draft_df.loc[draft_df.Retired == 0, "To"].value_counts())

# Mike Kafka is retired according to wikipedia, but PFR still has him
draft_df.loc[draft_df.Player == "Mike Kafka", "Retired"] = 1

# function calculate the career duration for each player
def calc_duration(player):
    """
    Calculte the years played for a player. If the 'To' value is 0 then return
    the value 0.  Otherwise set that column value to equal
    'To' - 'Draft_Yr' + 1.
    """

    # The player never played a season if their "To" value is 0, so return 0
    if player["To"] == 0:
        return 0

    # Otherwise return the number of years they played.
    duration = player["To"] - player["Draft_Yr"] + 1
    return duration

# Now create a Duration column, by applying the above function to each
# row, which represents a player
# to apply the function to each row, you must use axis=1
draft_df["Duration"]  = draft_df.apply(lambda player: calc_duration(player),
                                           axis=1)

#print (draft_df.head())

# convert some colums from float to int# conver
cols_to_int = ['Age', 'To', 'G', 'Cmp', 'Att', 'Yds', 'TD', 'Int',
               'Rush_Att', 'Rush_Yds', 'Rush_TD', 'Rec', 'Rec_Yds', 'Rec_TD',
               'Def_Int', 'Duration']

draft_df.loc[:, cols_to_int] = draft_df.loc[:, cols_to_int].astype(int)

#print(draft_df.info())

draft_df.to_csv("nfl_survival_analysis_data.csv", index=False)
