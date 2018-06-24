import html5lib
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import sys

# url that we are scraping
url = "http://www.basketball-reference.com/draft/NBA_2014.html"
# this is the html from the given url
html = urlopen(url)
#create BeautifulSoup obj
soup = BeautifulSoup(html, "html5lib")
column_headers = [th.getText() for th in
                  soup.findAll('tr', limit=2)[1].findAll('th')]
#column_headers.remove(column_headers[0])
#data_rows = soup.findAll('tr')[2:]  # skip the first 2 header rows
#player_data = [[td.getText() for td in data_rows[i].findAll('td')]
#            for i in range(len(data_rows))]
#df = pd.DataFrame(player_data, columns=column_headers)
#df = df[df.Player.notnull()]
#df.rename(columns={'WS/48':'WS_per_48'}, inplace=True)
# get the column names and replace all '%' with '_Perc'
#df.columns = df.columns.str.replace('%', '_Perc')
# Get the columns we want by slicing the list of column names
# and then replace them with the appended names
#df.columns.values[14:18] = [df.columns.values[14:18][col] +
#                                  "_per_G" for col in range(4)]
#df = df.convert_objects(convert_numeric=True)
#df = df[:].fillna(0) # index all the columns and fill in the 0s
#df.loc[:,'Yrs':'AST'] = df.loc[:,'Yrs':'AST'].astype(int)
#df.insert(0, 'Draft_Yr', 2014)
#df.drop('Rk', axis='columns', inplace=True)

url_template = "http://www.basketball-reference.com/draft/NBA_{year}.html"
# create an empty DataFrame
draft_df = pd.DataFrame()
for year in range(1966, 2018):  # for each year
    url = url_template.format(year=year)  # get the url

    html = urlopen(url)  # get the html
    soup = BeautifulSoup(html, 'html5lib') # create our BS object

    # get our player data
    data_rows = soup.findAll('tr')[2:]
    player_data = [[td.getText() for td in data_rows[i].findAll(['td','th'])]
                for i in range(len(data_rows))]

    # Turn yearly data into a DatFrame
    year_df = pd.DataFrame(player_data, columns=column_headers)
    # create and insert the Draft_Yr column
    year_df.insert(0, 'Draft_Yr', year)

    # Append to the big dataframe
    draft_df = draft_df.append(year_df, ignore_index=True)

# Convert data to proper data types
draft_df = draft_df.convert_objects(convert_numeric=True)

# Get rid of the rows full of null values
draft_df = draft_df[draft_df.Player.notnull()]

# Replace NaNs with 0s
draft_df = draft_df.fillna(0)

# Rename Columns
draft_df.rename(columns={'WS/48':'WS_per_48'}, inplace=True)
# Change % symbol
draft_df.columns = draft_df.columns.str.replace('%', '_Perc')
# Add per_G to per game stats
draft_df.columns.values[15:19] = [draft_df.columns.values[15:19][col] +
                                  "_per_G" for col in range(4)]

# Changing the Data Types to int
draft_df.loc[:,'Yrs':'AST'] = draft_df.loc[:,'Yrs':'AST'].astype(int)

# Delete the 'Rk' column
draft_df.drop('Rk', axis='columns', inplace=True)

draft_df['Pk'] = draft_df['Pk'].astype(int) # change Pk to int

draft_df.to_csv("draft_data_1966_to_2018.csv")
