
# Libraries
import csv
import datetime
import math
import logging
import requests

import pandas as pd

from time import sleep


logger = logging.getLogger("OSRS_GE_ML")


def collect_item_graph_data_and_write_to_csv(base_url, endpoint, item_id, file_name):
    url = base_url + endpoint.format(item_id)
    logger.info("Collecting item graph data from: {}".format(url))

    with requests.Session() as sesh:

        with open(file_name, "w", newline="") as csvfile:
            field_names = ["Timestamp", "Item Value Daily", "Item Value Average"]
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()

            response = fetch_response(sesh, url)
            response_json = fetch_json(sesh, url, response)

            data_daily = response_json["daily"]
            data_average = response_json["average"]

            for key in sorted(data_daily.keys()):
                timestamp = datetime.datetime.fromtimestamp(int(key)/1000.0).date()
                value_daily = data_daily[key]
                value_average = data_average[key]

                writer.writerow({
                    "Timestamp": timestamp,
                    "Item Value Daily": value_daily,
                    "Item Value Average": value_average
                })


def collect_item_ids(base_url, endpoint_catalogue_category, endpoint_catalogue_items, file_name):
    url_category = base_url + endpoint_catalogue_category
    logger.info("Collecting catalogue category data from: {}".format(url_category))

    with requests.Session() as sesh:

        with open(file_name, "w", newline="") as csvfile:
            field_names = ["Id", "Name"]
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()

            response_category = fetch_response(sesh, url_category)
            response_category_json = fetch_json(sesh, url_category, response_category)

            data_alpha = response_category_json["alpha"]
            for entry in data_alpha:
                letter = entry["letter"]
                items = entry["items"]

                # The API cannot parse # so use %23
                if letter == "#":
                    letter = "%23"

                # If there are multiple pages iterate over them
                for page in range(1, int(math.ceil(items / 12.0))):
                    url_items = base_url + endpoint_catalogue_items.format(letter, page)
                    logger.info("Collecting catalogue item data from: {}".format(url_items))
                    response_items = fetch_response(sesh, url_items)
                    response_items_json = fetch_json(sesh, url_items, response_items)

                    for item in response_items_json["items"]:
                        writer.writerow({
                            "Id": item["id"],
                            "Name": item["name"]
                        })


def collect_promising_items(base_url, df_items: pd.DataFrame, endpoint_catalogue_detail, file_name):
    with requests.Session() as sesh:

        with open(file_name, "w", newline="") as csvfile:
            field_names = ["Id", "Name", "DayTrend30", "Members", "Price"]
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()

            for index, data in df_items.iterrows():
                item_id = data["Id"]
                item_name = data["Name"]

                url_item = base_url + endpoint_catalogue_detail.format(item_id)
                logger.info("Determining if item: {} [{}] looks promising".format(item_name, item_id))

                response_item = fetch_response(sesh, url_item)
                response_item_json = fetch_json(sesh, url_item, response_item)

                item_detail = response_item_json["item"]
                current = item_detail["current"]
                day30 = item_detail["day30"]
                day90 = item_detail["day90"]
                day180 = item_detail["day180"]

                recent_trends = [
                    # current["trend"],
                    day30["trend"],
                    # day90["trend"],
                    # day180["trend"]
                ]

                if "positive" in recent_trends:
                    writer.writerow({
                        "Id": item_id,
                        "Name": item_name,
                        "DayTrend30": day30["change"],
                        "Members": item_detail["members"],
                        "Price": translate_number(current["price"])
                    })

                sleep(4)


def fetch_response(sesh, url_item):
    status_code = 0
    attempt = 1
    while status_code != 200:
        response = sesh.get(url_item)
        status_code = response.status_code
        if status_code != 200:
            logger.error("Returned non-200 status code, waiting to try again. Attempt {}".format(attempt))
            sleep(5)
            attempt += 1

    return response


def fetch_json(sesh, url_item, response):
    is_empty = True
    attempt = 1
    while is_empty:
        try:
            response_json = response.json()
            is_empty = False

        except ValueError:
            logger.error("Returned empty json, waiting to try again, Attempt {}".format(attempt))
            sleep(5)
            response = fetch_response(sesh, url_item)
            attempt += 1

    return response_json


def translate_number(num_in):
    end_char = num_in[-1]
    if end_char in ["k", "m", "b"]:
        num_actual = num_in[:-1]

        if end_char == "k":
            num_actual *= int(num_actual * 1_000)

        elif end_char == "m":
            num_actual *= int(num_actual * 1_000_000)

        elif end_char == "b":
            num_actual = int(num_actual * 1_000_000_000)
    else:
        num_actual = int(num_in)

    return num_actual
