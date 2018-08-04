This Repository is to scrape the web for different Sports Data.

Draft.py uses BeautifulSoup to scrape basketball-reference for all the nba draft data from 1966 until 2017 and then it saves it to a csv file. Visualizing_draft_nba.py reads the csv file and makes graphs based on the data. There are line graphs, bar graphs, box plots, and violin graphs showing various trends in the nba draft.

Nfl_draft.py gets the draft data from football-reference for all the nfl draft data from 1967 until 2018 and cleans the data and saves it to a csv file. It also graphs the data to show various trends in the nfl draft.

The data_prep.py preps nfl draft data for a survival analysis and then survival_function_nfl.py makes graphs and shows the survival function for different positions in the NFL.

Used a tutorial from Savvas Tjortjoglou for guidance.
