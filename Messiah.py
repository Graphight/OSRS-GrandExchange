
# Import Libraries
import warnings
import itertools
import logging
import numpy as np
import matplotlib.pyplot as plt
from pylab import rcParams

import pandas as pd
import statsmodels.api as sm
import matplotlib

from fbprophet import Prophet

from DataCollection import collect_item_graph_data_and_write_to_csv
from Functions_Model import determine_best_p_d_q_variables


# =================================================
#  ========== PRELIM : CONFIG MATPLOTLIB ==========
# =================================================
warnings.filterwarnings("ignore")
plt.style.use("fast")
matplotlib.rcParams["axes.labelsize"] = 14
matplotlib.rcParams["xtick.labelsize"] = 12
matplotlib.rcParams["ytick.labelsize"] = 12
matplotlib.rcParams["text.color"] = "k"
matplotlib.rcParams["figure.figsize"] = 18, 8


# Important
BASE_URL = "http://services.runescape.com/m=itemdb_oldschool"


# Endpoints
ITEM_DETAIL = "/api/catalogue/detail.json?item={}"
ITEM_GRAPHS = "/api/graph/{}.json"

# Item dict
items = {"Bow string": 440}

logger = logging.getLogger('OSRS_GE_ML')
logger.setLevel(logging.DEBUG)


# =================================================
#     ========== STEP ONE : GET DATA ==========
# =================================================
file_name = "test.csv"
collect_item_graph_data_and_write_to_csv(BASE_URL, ITEM_GRAPHS, 453, file_name)
df = pd.read_csv(file_name)
logger.info("STEP ONE COMPLETE: Data Collected")


# =================================================
#   ========== STEP TWO : PROCESS DATA ==========
# =================================================
df = df.sort_values("Timestamp")
df = df.set_index("Timestamp")
df.index = pd.to_datetime(df.index)

freq = 7
sample_data = df["Item Value Daily"].resample(str(freq) + "D").mean()
decomposition = sm.tsa.seasonal_decompose(sample_data, model="additive", freq=freq)
decomposition.plot()
logger.info("STEP TWO COMPLETE: Data Processed")


# =================================================
# ========== STEP THREE : MODEL CREATION ==========
# =================================================
# Use Facebook"s -Prophet-
prophet_df = pd.DataFrame({"ds": df.index, "y": df["Item Value Daily"].values})
prophet_model = Prophet(interval_width=0.95)
prophet_model.fit(prophet_df)
logger.info("STEP THREE COMPLETE: Model Created")


# =================================================
#   ========== STEP FOUR : PREDICTIONS ==========
# =================================================
# Facebook's -Prophet-
graph_title = "OSRS Grand Exchange - Price prediction - Coal "
graph_x_label = "Timestamp"
graph_y_label = "Item Value Daily"

future_steps = 14
prophet_forecast = prophet_model.make_future_dataframe(periods=future_steps, freq="D", include_history=True)
prophet_forecast = prophet_model.predict(prophet_forecast)

prophet_model.plot(prophet_forecast, xlabel=graph_x_label, ylabel=graph_y_label)
plt.title(graph_title + "< Prophet Forecast >")
plt.legend()

logger.info("STEP FOUR COMPLETE: Predictions Made")


# =================================================
#    ========== STEP FIVE : EVALUATION ==========
# =================================================
# Verdicts
length = len(df.index)
verdict = ""
for i in range(0, future_steps):
    index = length + i
    current = prophet_forecast.iloc[index]["yhat"]
    previous = prophet_forecast.iloc[index - 1]["yhat"]
    percentage = ((current / previous) - 1) * 100
    if current > previous:
        verdict = "Increase"
    else:
        verdict = "Decrease"
    print("{} - \t{:.2f} to \t{:.2f} -> \t{:.2f} %".format(verdict, previous, current, percentage))


# Trends and patterns -Prophet-
prophet_model.plot_components(prophet_forecast)
plt.show()
logger.info("STEP FIVE COMPLETE: Evaluation Complete")











