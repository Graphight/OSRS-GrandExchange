
# Libraries
import warnings
import pandas as pd
import statsmodels.api as sm

import itertools
import logging
import matplotlib

from time import sleep
from matplotlib import pyplot as plt
from DataCollection import collect_item_graph_data_and_write_to_csv, collect_item_ids, collect_promising_items
from Messiah import Messiah


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


# =================================================
#     ========== STEP ONE : SETUP ==========
# =================================================

# Important
BASE_URL = "http://services.runescape.com/m=itemdb_oldschool"
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("OSRS_GE_ML")
logger.setLevel("DEBUG")

# Endpoints
ENDPOINT_CATALOGUE_CATEGORY = "/api/catalogue/category.json?category=1"
ENDPOINT_CATALOGUE_ITEMS = "/api/catalogue/items.json?category=1&alpha={}&page={}"
ENDPOINT_CATALOGUE_DETAIL = "/api/catalogue/detail.json?item={}"
ENDPOINT_GRAPHS = "/api/graph/{}.json"


# =================================================
#     ========== STEP TWO : DISCOVERY ==========
# =================================================
last_index = 0


# Collect item ids
file_name_ids = "ItemIds.csv"
file_name_promising = "ItemsPromising.csv"
# collect_item_ids(BASE_URL, ENDPOINT_CATALOGUE_CATEGORY, ENDPOINT_CATALOGUE_ITEMS, file_name)

df_item_ids = pd.read_csv(file_name_ids)
collect_promising_items(BASE_URL, df_item_ids, ENDPOINT_CATALOGUE_DETAIL, file_name_promising, last_index)

df_items_promising = pd.read_csv(file_name_promising)
df_items_promising["DayTrend30Float"] = df_items_promising["DayTrend30"].apply(lambda x: float(x[1:-1]))

df_items_promising_sorted = df_items_promising.copy()
df_items_promising_sorted.sort_values("DayTrend30Float", ascending=False, inplace=True)
# print(df_items_promising_sorted.head())

# df_top_5_items = df_items_promising_sorted.head(20)
# print(df_top_5_items)

# messiah = Messiah(BASE_URL, ENDPOINT_GRAPHS, ENDPOINT_CATALOGUE_DETAIL, df_top_5_items, "temp.csv")
# messiah.run_items()


# messiah.current_item_name = "Lobster"
# messiah.current_item_name = "Lobster Pot"
# messiah.current_item_id = 379
# messiah.current_item_id = 301
# messiah.run()



























