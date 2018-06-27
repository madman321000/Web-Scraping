import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from lifelines import KaplanMeierFitter

draft_df = pd.read_csv("nfl_survival_analysis_data.csv")

# set some plotting aesthetics, similar to ggplot
sns.set(palette = "colorblind", font_scale = 1.35,
        rc = {"figure.figsize": (12,9), "axes.facecolor": ".92"})

#print(draft_df.head())

kmf = KaplanMeierFitter()

# The 1st arg accepts an array or pd.Series of individual survival times
# The 2nd arg accepts an array or pd.Series that indicates if the event
# interest (or death) occured.
kmf.fit(durations = draft_df.Duration,
        event_observed = draft_df.Retired)

#print(kmf.event_table())

# get the values for time = 0 from the survival table
event_at_0 = kmf.event_table.iloc[0, :]
# now calculate the survival probability for t = 0
surv_for_0 =  (event_at_0.at_risk - event_at_0.observed) / event_at_0.at_risk

# Calculate the survival probability for t = 1
event_at_1 = kmf.event_table.iloc[1, :]
surv_for_1 =  (event_at_1.at_risk - event_at_1.observed) / event_at_1.at_risk

# Calculate the survival probability for t = 2
event_at_2 = kmf.event_table.iloc[2, :]
surv_for_2 =  (event_at_2.at_risk - event_at_2.observed) / event_at_2.at_risk

# The probability that an NFL player has a career longer than 2 years
surv_after_2 = surv_for_0 * surv_for_1 * surv_for_2

kmf.predict(2)

# The survival probabilities of NFL players after 1, 3, 5, and 10 yrs played
kmf.predict([1,3,5,10])

kmf.survival_function_

kmf.median_

# plot the KM estimate
kmf.plot()
# Add title and y-axis label
plt.title("The Kaplan-Meier Estimate for Drafted NFL Players\n(1967-2015)")
plt.ylabel("Probability a Player is Still Active")

plt.show()

#print (draft_df.Pos.unique()) # check out all the different positions

# Relabel/Merge some of the positions
# Set all HBs to RB
draft_df.loc[draft_df.Pos == "HB", "Pos"] = "RB"

# Set all Safeties and Cornernbacks to DBs
draft_df.loc[draft_df.Pos.isin(["SS", "FS", "S", "CB"]), "Pos"] = "DB"

# Set all types of Linebackers to LB
draft_df.loc[draft_df.Pos.isin(["OLB", "ILB"]), "Pos"] = "LB"

# drop players from the following positions [FL, E, WB, KR, LS, OL]
# get the row indices for players with undesired postions
idx = draft_df.Pos.isin(["FL", "E", "WB", "KR", "LS", "DL", "OL", "Pos"])
# keep the players that don't have the above positions
draft_df_2 = draft_df.loc[~idx, :]

# check the number of positions in order to decide
# on the plotting grid dimiensions
#print (draft_df_2.Pos.unique())

# create a new KMF object
kmf_by_pos = KaplanMeierFitter()

duration = draft_df_2.Duration
observed = draft_df_2.Retired

# Set the order that the positions will be plotted
positions = ["QB", "RB", "WR",
             "TE", "T", "G",
             "C", "DE", "DT",
             "NT", "LB", "DB",
             "FB", "K", "P"]

# Set up the the 5x3 plotting grid by creating figure and axes objects
# Set sharey to True so that each row of plots share the left most y-axis labels
fig, axes = plt.subplots(nrows = 5, ncols = 3, sharey = True,
                         figsize=(12,15))

# flatten() creates a 1-D array of the individual axes (or subplots)
# that we will plot on in our grid
# We zip together the two 1-D arrays containing the positions and axes
# so we can iterate over each postion and plot its KM estimate onto
# its respective axes
for pos, ax in zip(positions, axes.flatten()):
    # get indices for players with the matching position label
    idx = draft_df_2.Pos == pos
    # fit the kmf for the those players
    kmf_by_pos.fit(duration[idx], observed[idx])
    # plot the KM estimate for that position on its respective axes
    kmf_by_pos.plot(ax=ax, legend=False)
    # place text indicating the median for the position
    # the xy-coord passed in represents the fractional value for each axis
    # for example (.5, .5) places text at the center of the plot
    ax.annotate("Median = {:.0f} yrs".format(kmf_by_pos.median_), xy = (.47, .85),
                xycoords = "axes fraction")
    # get rid the default "timeline" x-axis label set by kmf.plot()
    ax.set_xlabel("")
    # label each plot by its position
    ax.set_title(pos)
    # set a common x and y axis across all plots
    ax.set_xlim(0,25)
    ax.set_ylim(0,1)

# tighten up the padding for the subplots
fig.tight_layout()

# https://stackoverflow.com/questions/16150819/common-xlabel-ylabel-for-matplotlib-subplots
# set a common x-axis label
fig.text(0.5, -0.01, "Timeline (Years)", ha="center")
# set a common y-axis label
fig.text(-0.01, 0.5, "Probability That a Player is Still Active",
         va="center", rotation="vertical")
# add the title for the whole plot
fig.suptitle("Survival Curve for each NFL Position\n(Players Drafted from 1967-2015)",
             fontsize=15)
# add some padding between the title and the rest of the plot to avoid overlap
fig.subplots_adjust(top=0.92)

plt.show()
