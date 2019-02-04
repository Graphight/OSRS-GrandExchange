
from requests import get
import csv
import datetime


def collect_item_graph_data_and_write_to_csv(base_url, endpoint, item_id, file_name):
    # Setup
    url = base_url + endpoint.format(item_id)

    print(url)

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
            timestamp = datetime.datetime.fromtimestamp(int(key)/1000.0)
            value_daily = data_daily[key]
            value_average = data_average[key]

            writer.writerow({"Timestamp": timestamp,
                             "Item Value Daily": value_daily,
                             "Item Value Average": value_average
                             })


