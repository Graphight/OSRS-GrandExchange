
# Libraries
import csv
import datetime
import math
import logging

import pandas as pd

from requests import get
from time import sleep


logger = logging.getLogger("OSRS")


def collect_item_graph_data_and_write_to_csv(base_url, endpoint, item_id, file_name):
    # Setup
    url = base_url + endpoint.format(item_id)
    print("Collecting item graph data from: {}".format(url))

    # Collect
    response = get(url).json()

    # Write to file
    with open(file_name, "w", newline="") as csvfile:
        field_names = ["Timestamp", "Item Value Daily", "Item Value Average"]
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()

        data_daily = response["daily"]
        data_average = response["average"]

        for key in sorted(data_daily.keys()):
            timestamp = datetime.datetime.fromtimestamp(int(key)/1000.0).date()
            value_daily = data_daily[key]
            value_average = data_average[key]

            writer.writerow({"Timestamp": timestamp,
                             "Item Value Daily": value_daily,
                             "Item Value Average": value_average
                             })


def collect_item_ids(base_url, endpoint_catalogue_category, endpoint_catalogue_items, file_name):
    # Sift through category data
    url_category = base_url + endpoint_catalogue_category
    print("Collecting catalogue category data from: {}".format(url_category))
    response_category = get(url_category).json()

    with open(file_name, "w", newline="") as csvfile:
        field_names = ["Item Id", "Item Name"]
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()

        data_alpha = response_category["alpha"]
        for entry in data_alpha:
            letter = entry["letter"]
            items = entry["items"]

            # The API cannot parse # so use %23
            if letter == "#":
                letter = "%23"

            # If there are multiple pages iterate over them
            for page in range(1, int(math.ceil(items / 12.0))):
                url_items = base_url + endpoint_catalogue_items.format(letter, page)
                print("Collecting catalogue item data from: {}".format(url_items))
                response_items = get(url_items).json()

                # Sift through each item and glean the id
                for item in response_items["items"]:
                    writer.writerow({"Item Id": item["id"],
                                     "Item Name": item["name"]
                                     })

                # Wait for a little between API calls
                sleep(1)


def collect_promising_items(base_url, df_items: pd.DataFrame, endpoint_catalogue_detail):
    promising = dict()

    for index, data in df_items.iterrows():
        item_id = data["Item Id"]
        item_name = data["Item Name"]

        url_item = base_url + endpoint_catalogue_detail.format(item_id)
        print("Determining if item: {} [{}] looks promising".format(item_name, item_id))
        response_item = get(url_item).json()

        item_detail = response_item["item"]
        current = item_detail["current"]
        day30 = item_detail["day30"]

        if "positive" in [current["trend"], day30["trend"]]:
            promising[item_name] = {
                "id": item_id,
                "trend": day30["change"],
                "members": item_detail["members"]
            }

        # sleep(0.5)

    return promising



