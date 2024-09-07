# Yahoo

> **ATTENTION!** Yahoo has taken away the ability to use the bees without an account, so currently the script will not work!

This is a simple python script that I use to get a monthly `.csv` file for a periodic update of my investments. For each month between the `startPeriod` and the `endPeriod` the script extracts the field `fieldToExtractFromCsv` for the day specified in the `dayToAnalyze` field.

## Usage

`python etf-yahoo.py <file_name>.json`

## Input

The script accept only **one** file in `.json` format with the following fields:

| field                 |  type   | values                                                  | obligatory | default value | example                          |
| --------------------- | :-----: | ------------------------------------------------------- | :--------: | :-----------: | -------------------------------- |
| outFileName           | string  | -                                                       |    yes     |    `empty`    | output.csv                       |
| overwriteOutputFile   | string  | `true`/`false`                                          |    yes     |    `false`    | true                             |
| dayToAnalyze          | integer | `1-31`                                                  |    yes     |    `empty`    | 31                               |
| frequency             | string  | `daily`/`weekly`/`monthly`                              |     no     |    `daily`    | daily                            |
| startPeriod           | string  | `yyyy/mm/dd`                                            |    yes     |    `empty`    | 2022/01/01                       |
| endPeriod             | string  | `yyyy/mm/dd`                                            |     no     |    `<now>`    | 2022/12/31                       |
| fieldToExtractFromCsv | string  | `Date`/`Open`/`High`/`Low`/`Close`/`Adj Close`/`Volume` |    yes     |    `empty`    | Adj Close                        |
| tickers               |  array  | -                                                       |    yes     |    `empty`    | ["AAPL", "BTC-USD", "USDEUR=X",] |

### Example

```json
{
  "outFileName": "output.csv",
  "overwriteOutputFile": "true",
  "dayToAnalyze": 31,
  "frequency": "daily",
  "startPeriod": "2022/01/01",
  "endPeriod": "2022/12/31",
  "fieldToExtractFromCsv": "Adj Close",
  "tickers": ["AAPL", "BTC-USD", "USDEUR=X"]
}
```

## Output

This a sample of the `.csv` file that the script generate

```csv
ticker,<MMM>-<YYYY>,<MMM>-<YYYY>,<MMM>-<YYYY>,<MMM>-<YYYY>
```

## Workflow

```text
1. Read the .json file
2. If the output file doesn't exist it will be created with the header
3. For each tickers:
    1. Download from yahoo finances the file with the specified data (url: https://query1.finance.yahoo.com)
    2. Read from the file the specified field
    3. Add a row in the output file with the field for each months between startPeriod and endPeriod
```
