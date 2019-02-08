
# Libraries]
import warnings
import pandas as pd
import statsmodels.api as sm

import itertools
import matplotlib
from matplotlib import pyplot as plt

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
items = {"Bow string": 1777}


# =================================================
#     ========== STEP ONE : GET DATA ==========
# =================================================
file_name = "test.csv"
collect_item_graph_data_and_write_to_csv(BASE_URL, ITEM_GRAPHS, 1777, file_name)
df = pd.read_csv(file_name)


# =================================================
#   ========== STEP TWO : PROCESS DATA ==========
# =================================================
df = df.sort_values("Timestamp")
df = df.set_index("Timestamp")
df.index = pd.to_datetime(df.index)

freq = 7
sample_data = df["Item Value Daily"].resample(str(freq) + "D").mean()
decomposition = sm.tsa.seasonal_decompose(sample_data, freq=freq)
decomposition.plot()


# =================================================
# ========== STEP THREE : MODEL CREATION ==========
# =================================================
# ARIMA stuff
arima_pdq = determine_best_p_d_q_variables(sample_data)
arima_model = arima_pdq.fit(disp=False)
# print(arima_model.summary().tables[1])
# arima_model.plot_diagnostics(figsize=(16, 8))


# =================================================
#   ========== STEP FOUR : PREDICTIONS ==========
# =================================================
# ARIMA stuff
length = len(df.index) / 7
# start_pred = pd.Timestamp.now().date() - pd.Timedelta(days=30)
# end_pred = pd.Timestamp.now().date()
arima_prediction = arima_model.get_prediction(start=int(length * 0.8), end=int(length + 10), dynamic=False)
arima_prediction_ci = arima_prediction.conf_int()

ax = df.plot(label="Observed")
arima_prediction.predicted_mean.plot(ax=ax, label="One-step ahead Forecast", alpha=0.8)

ax.fill_between(arima_prediction_ci.index,
                arima_prediction_ci.iloc[:, 0],
                arima_prediction_ci.iloc[:, 1], color='k', alpha=0.2)
ax.set_xlabel("Timestamp")
ax.set_ylabel("Closing Price")
plt.legend()


# =================================================
#    ========== STEP FIVE : EVALUATION ==========
# =================================================
# ARIMA MSE
# arima_forecast = arima_prediction.predicted_mean[:(end_pred - pd.DateOffset(minutes=10))]
# arima_truth = sample_data[start_pred:]
# mse = ((arima_forecast - arima_truth) ** 2).mean()
# print("The Mean Square Error of our forecast is {}".format(round(mse, 2)))

plt.show()


