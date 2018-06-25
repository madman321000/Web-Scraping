import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import html5lib
# set some plotting styles
from matplotlib import rcParams

from urllib.request import urlopen
from bs4 import BeautifulSoup

def extract_player_data(table_rows):
    """
    Extract and return the the desired information from the td elements within
    the table rows.
    """
    # create the empty list to store the player data
    player_data = []

    for row in table_rows:  # for each row do the following

        # Get the text for each table data (td) element in the row
        # Some player names end with ' HOF', if they do, get the text excluding
        # those last 4 characters,
        # otherwise get all the text data from the table data
        player_list = [td.get_text()[:-4] if td.get_text().endswith(" HOF")
                       else td.get_text() for td in row.find_all(['th' , 'td'])]

        # there are some empty table rows, which are the repeated
        # column headers in the table
        # we skip over those rows and and continue the for loop
        if not player_list:
            continue

        # Extracting the player links
        # Instead of a list we create a dictionary, this way we can easily
        # match the player name with their pfr url
        # For all "a" elements in the row, get the text
        # NOTE: Same " HOF" text issue as the player_list above
        links_dict = {(link.get_text()[:-4]   # exclude the last 4 characters
                       if link.get_text().endswith(" HOF")  # if they are " HOF"
                       # else get all text, set thet as the dictionary key
                       # and set the url as the value
                       else link.get_text()) : link["href"]
                       for link in row.find_all("a", href=True)}

        # The data we want from the dictionary can be extracted using the
        # player's name, which returns us their pfr url, and "College Stats"
        # which returns us their college stats page

        # add the link associated to the player's pro-football-reference page,
        # or en empty string if there is no link
        player_list.append(links_dict.get(player_list[3], ""))

        # add the link for the player's college stats or an empty string
        # if ther is no link
        player_list.append(links_dict.get("College Stats", ""))

        # Now append the data to list of data
        player_data.append(player_list)

    return player_data
# Create an empty list that will contain all the dataframes
# (one dataframe for each draft)
draft_dfs_list = []

# a list to store any errors that may come up while scraping
errors_list = []

# The url template that we pass in the draft year inro
url_template = "http://www.pro-football-reference.com/years/{year}/draft.htm"

# for each year from 1967 to (and including) 2016
for year in range(1967, 2018):

    # Use try/except block to catch and inspect any urls that cause an error
    try:
        # get the draft url
        url = url_template.format(year=year)

        # get the html
        html = urlopen(url)

        # create the BeautifulSoup object
        soup = BeautifulSoup(html, "html5lib")

        # get the column headers
        column_headers = [th.getText() for th in
                          soup.findAll('tr', limit=2)[1].findAll('th')]
        column_headers.extend(["Player_NFL_Link", "Player_NCAA_Link"])

        # select the data from the table using the '#drafts tr' CSS selector
        table_rows = soup.select("#drafts tr")[2:]

        # extract the player data from the table rows
        player_data = extract_player_data(table_rows)

        # create the dataframe for the current years draft
        year_df = pd.DataFrame(player_data, columns=column_headers)

        # if it is a draft from before 1994 then add a Tkl column at the
        # 24th position
        if year < 1994:
            year_df.insert(24, "Tkl", "")

        # add the year of the draft to the dataframe
        year_df.insert(0, "Draft_Yr", year)

        # append the current dataframe to the list of dataframes
        draft_dfs_list.append(year_df)

    except Exception as e:
        # Store the url and the error it causes in a list
        error =[url, e]
        # then append it to the list of errors
        errors_list.append(error)
# store all drafts in one DataFrame
draft_df = pd.concat(draft_dfs_list, ignore_index=True)

# Take a look at the first few rows
#print(draft_df.head())

# get the current column headers from the dataframe as a list
column_headers = draft_df.columns.tolist()

# The 5th column header is an empty string, but represesents player names
column_headers[4] = "Player"

# Prepend "Rush_" for the columns that represent rushing stats
column_headers[19:22] = ["Rush_" + col for col in column_headers[19:22]]

# Prepend "Rec_" for the columns that reperesent receiving stats
column_headers[23:25] = ["Rec_" + col for col in column_headers[23:25]]

# Properly label the defensive int column as "Def_Int"
column_headers[-6] = "Def_Int"

# Just use "College" as the column header represent player's colleger or univ
column_headers[-4] = "College"

# Take a look at the updated column headers
#print(column_headers)

# Now assign edited columns to the DataFrame
draft_df.columns = column_headers

# Write out the raw draft data
#draft_df.to_csv("pfr_nfl_draft_data_RAW.csv")

# extract the player id from the player links
# expand=False returns the IDs as a pandas Series
player_ids = draft_df.Player_NFL_Link.str.extract("/.*/.*/(.*)\.",
                                                  expand=False)

# add a Player_ID column to our draft_df
draft_df["Player_ID"] = player_ids

# add the beginning of the pfr url to the player link column
pfr_url = "http://www.pro-football-reference.com"
draft_df.Player_NFL_Link =  pfr_url + draft_df.Player_NFL_Link

# Get the Player name, IDs, and links
player_id_df = draft_df.loc[:, ["Player", "Player_ID", "Player_NFL_Link",
                                "Player_NCAA_Link"]]
# Save them to a CSV file
#player_id_df.to_csv("pfr_player_ids_and_links.csv")

# drop the the player links and the column labeled by an empty string
draft_df.drop(draft_df.columns[-4:-1], axis=1, inplace=True)

# convert the data to proper numeric types
draft_df = draft_df.convert_objects(convert_numeric=True)

#print(draft_df.info())

# Get the column names for the numeric columns
num_cols = draft_df.columns[draft_df.dtypes != object]

# Replace all NaNs with 0
draft_df.loc[:, num_cols] = draft_df.loc[:, num_cols].fillna(0)

#draft_df.to_csv("pfr_nfl_draft_data_CLEAN.csv", index=False)

# get data for drafts from 1967 to 2010
draft_df_2010 = draft_df.loc[draft_df.Draft_Yr <= 2010, :]

#print(draft_df_2010.tail())

# set the font scaling and the plot sizes
sns.set(font_scale=1.65)
rcParams["figure.figsize"] = 12,9

# Use distplot to view the distribu
sns.distplot(draft_df_2010.CarAV)
plt.title("Distribution of Career Approximate Value")
plt.xlim(-5,150)
plt.show()

# drop players from the following positions [FL, E, WB, KR]
drop_idx = ~ draft_df_2010.Pos.isin(["FL", "E", "WB", "KR"])

draft_df_2010 = draft_df_2010.loc[drop_idx, :]

# Now replace HB label with RB label
draft_df_2010.loc[draft_df_2010.Pos == "HB", "Pos"] = "RB"

sns.boxplot(x="Pos", y="CarAV", data=draft_df_2010)
plt.title("Distribution of Career Approximate Value by Position (1967-2010)")
plt.show()

# plot LOWESS curve
# set line color to be black, and scatter color to cyan
sns.regplot(x="Pick", y="CarAV", data=draft_df_2010, lowess=True,
            line_kws={"color": "black"},
            scatter_kws={"color": sns.color_palette()[5], "alpha": 0.5})
plt.title("Career Approximate Value by Pick")
plt.xlim(-5, 500)
plt.ylim(-5, 200)
plt.show()

# Fit a LOWESS curver for each position
sns.lmplot(x="Pick", y="CarAV", data=draft_df_2010, lowess=True, hue="Pos",
           size=10, scatter=False)
plt.title("Career Approximate Value by Pick and Position")
plt.xlim(-5, 500)
plt.ylim(-1, 60)
plt.show()

lm = sns.lmplot(x="Pick", y="CarAV", data=draft_df_2010, lowess=True, col="Pos",
                col_wrap=5, size=4, line_kws={"color": "black"},
                scatter_kws={"color": sns.color_palette()[5], "alpha": 0.7})

# add title to the plot (which is a FacetGrid)
# https://stackoverflow.com/questions/29813694/how-to-add-a-title-to-seaborn-facet-plot
plt.subplots_adjust(top=0.9)
lm.fig.suptitle("Career Approximate Value by Pick and Position",
                fontsize=30)

plt.xlim(-5, 500)
plt.ylim(-1, 100)
plt.show()
