
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


class Messiah:

    def __init__(self, base_url, endpoint_graph, endpoint_detail, df_items, file_name):
        # API interaction
        self.base_url = base_url
        self.endpoint_graph = endpoint_graph
        self.endpoint_detail = endpoint_detail

        # Data Objects
        self.df_items = df_items
        self.df = None
        self.df_sampled = None
        self.df_prohpet = None
        self.prophet_model = None
        self.prophet_forecast = None
        
        # Tuning
        self.seasonal_freq = 7
        self.prediction_steps = 10

        # Misc
        self.file_name = file_name
        self.current_item_id = None
        self.current_item_name = None
        self.logger = logging.getLogger("OSRS_GE_ML")

    # =================================================
    #     ========== STEP ONE : GET DATA ==========
    # =================================================
    def step_one(self):
        collect_item_graph_data_and_write_to_csv(self.base_url, self.endpoint_graph, self.current_item_id, self.file_name)
        self.df = pd.read_csv(self.file_name)
        self.logger.info("STEP ONE COMPLETE: Data Collected")

    # =================================================
    #   ========== STEP TWO : PROCESS DATA ==========
    # =================================================
    def step_two(self):
        self.df = self.df.sort_values("Timestamp")
        self.df = self.df.set_index("Timestamp")
        self.df.index = pd.to_datetime(self.df.index)

        self.df_sampled = self.df["Item Value Daily"].resample(str(self.seasonal_freq) + "D").mean()
        decomposition = sm.tsa.seasonal_decompose(self.df_sampled, model="additive", freq=self.seasonal_freq)
        decomposition.plot()
        self.logger.info("STEP TWO COMPLETE: Data Processed")

    # =================================================
    # ========== STEP THREE : MODEL CREATION ==========
    # =================================================
    def step_three(self):
        self.df_prohpet = pd.DataFrame({"ds": self.df.index, "y": self.df["Item Value Daily"].values})
        self.prophet_model = Prophet(interval_width=0.95)
        self.prophet_model.fit(self.df_prohpet)
        self.logger.info("STEP THREE COMPLETE: Model Created")

    # =================================================
    #   ========== STEP FOUR : PREDICTIONS ==========
    # =================================================
    def step_four(self):
        graph_title = "OSRS Grand Exchange - Price prediction - {}".format(self.current_item_name)
        graph_x_label = "Timestamp"
        graph_y_label = "Item Value Daily"
    
        self.prophet_forecast = self.prophet_model.make_future_dataframe(periods=self.prediction_steps, freq="D", include_history=True)
        self.prophet_forecast = self.prophet_model.predict(self.prophet_forecast)
    
        self.prophet_model.plot(self.prophet_forecast, xlabel=graph_x_label, ylabel=graph_y_label)
        plt.title(graph_title)
        plt.legend()
    
        self.logger.info("STEP FOUR COMPLETE: Predictions Made")

    # =================================================
    #    ========== STEP FIVE : EVALUATION ==========
    # =================================================
    def step_five(self):
        length = len(self.df.index)
        for i in range(0, self.prediction_steps):
            index = length + i
            current = self.prophet_forecast.iloc[index]["yhat"]
            previous = self.prophet_forecast.iloc[index - 1]["yhat"]
            percentage = ((current / previous) - 1) * 100
            if current > previous:
                verdict = "Increase"
            else:
                verdict = "Decrease"
            print("{} - \t{:.2f} to \t{:.2f} -> \t{:.2f} %".format(verdict, previous, current, percentage))

        # Trends and patterns -Prophet-
        self.prophet_model.plot_components(self.prophet_forecast)
        plt.show()
        self.logger.info("STEP FIVE COMPLETE: Evaluation Complete")

    def reset(self):
        self.current_item_id = None
        self.current_item_name = None
        self.df = None
        self.df_sampled = None
        self.df_prohpet = None
        self.prophet_model = None
        self.prophet_forecast = None

    def run_items(self):
        for index, row in self.df_items.iterrows():
            # print(row)
            self.current_item_id = row["Id"]
            self.current_item_name = row["Name"]
            self.run()

    def run(self):
            self.step_one()
            self.step_two()
            self.step_three()
            self.step_four()
            self.step_five()
            self.reset()

