import sys
import os
import csv
import time
import requests
import json
import calendar
import pandas as pd
from datetime import datetime
from io import StringIO
from collections import defaultdict

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.3",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/123.0",
]
DEFAULT_DATE_FORMAT = "%Y/%m/%d"


def convert_to_unix_timestamp(date):
    return int(datetime.strptime(date, DEFAULT_DATE_FORMAT).timestamp())


def get_mode(overwrite_output_file):
    if overwrite_output_file:
        return "w"

    return "a"


def create_csv(file_name, overwrite_output_file, ticker, data):
    header_writed = false
    header = ["ticker"] + [item[0] for item in data]
    rows = [ticker] + [item[1] for item in data]

    with open(file_name, get_mode(overwrite_output_file)) as csvfile:
        csvwriter = csv.writer(csvfile)
        if not header_writed:
            csvwriter.writerow(header)
            header_writed = true

        csvwriter.writerow(rows)


def get_interval_for_remote_source(frequency):
    if frequency == "daily":
        return "1d"
    elif frequency == "weakly":
        return "1wk"
    else:
        return "1mo"


def download_csv(url):
    try:
        for i in range(len(USER_AGENTS)):
            if i > 0:
                print(f"Tentativo numero {i + 1}...")

            response = requests.get(url, headers={"User-agent": USER_AGENTS[i]})

            if response.status_code == 200:
                content = response.text
                return content
            else:
                print(
                    f"Errore durante il download del file CSV. Codice di stato: {response.status_code}"
                )
                print("Attendere 5 secondi prima di un nuovo tentativo")
                time.sleep(5)

        return None
    except Exception as e:
        print(f"Si è verificato un errore durante il download del file CSV: {e}")
        return None


def get_column_from_csv(csv_data, day_to_analyze, field_to_extract):
    df = pd.read_csv(StringIO(csv_data))

    df["Date"] = pd.to_datetime(df["Date"])
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Day"] = df["Date"].dt.day

    current_year = datetime.now().year
    current_month = datetime.now().month
    current_day = datetime.now().day

    results = []

    for index, row in df.iterrows():
        year = row["Year"]
        month = row["Month"]
        day = row["Day"]

        # if day_to_analyze == "":
        last_day_of_month = calendar.monthrange(year, month)[1]
        day_to_analyze = last_day_of_month

        if day == day_to_analyze:
            key = f"{datetime(year, month, 1).strftime('%b')}-{year}"
            results.append((key, row[field_to_extract]))
        elif index < df.index[-1]:
            next_row = df.iloc[index + 1]
            next_row_year = next_row["Year"]
            next_row_month = next_row["Month"]

            if (next_row_month < month and next_row_year > year) or (
                next_row_month > month and next_row_year == year
            ):
                key = f"{datetime(year, month, 1).strftime('%b')}-{year}"
                results.append((key, row[field_to_extract]))
        else:
            key = f"{datetime(year, month, 1).strftime('%b')}-{year}"
            results.append((key, row[field_to_extract]))

    return results


def process_etf(
    out_file_name,
    overwrite_output_file,
    day_to_analyze,
    frequency,
    start_period,
    end_period,
    field_to_extract,
    ticker,
):
    interval = get_interval_for_remote_source(frequency)

    unix_start_period = convert_to_unix_timestamp(start_period)
    unix_end_period = convert_to_unix_timestamp(end_period)

    url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={unix_start_period}&period2={unix_end_period}&interval={interval}&events=history&includeAdjustedClose=true"
    print(url)
    csv_data = download_csv(url)

    if csv_data is not None:
        values = get_column_from_csv(csv_data, day_to_analyze, field_to_extract)
        create_csv(out_file_name, overwrite_output_file, ticker, values)
    else:
        print(
            f"Errore - nessun csv trovato per il perido: {start_period} - {end_period}"
        )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_json_file>")
        sys.exit(1)

    with open(sys.argv[1], "r") as file:
        data = json.load(file)

    out_file_name = data.get("outFileName", "")
    overwrite_output_file = data.get("overwriteOutputFile", "false")
    day_to_analyze = data.get("dayToAnalyze", "")
    frequency = data.get("frequency", "daily")
    start_period = data.get("startPeriod", "")
    end_period = data.get(
        "endPeriod",
        f"{datetime.now().year}/{datetime.now().month}/{datetime.now().day}",
    )
    field_to_extract = data.get("fieldToExtractFromCsv", "Adj Close")
    tickers_list = data.get("tickers", [])

    for ticker in tickers_list:
        process_etf(
            out_file_name,
            overwrite_output_file,
            day_to_analyze,
            frequency,
            start_period,
            end_period,
            field_to_extract,
            ticker,
        )
