import pandas as pd
from datetime import datetime
import json
from copy import copy
import re


def convert_claim_json(claim_json: dict) -> dict:
    """
    Function used to convert data types in claim JSON's
    in appropriate way: string conversion to dates, replacing
    missing values with None, etc.

    :param claim_json: Raw JSON of claim.
    :return: Claim JSON with properly converted types.
    """
    date_pattern = r'^([0-2][0-9]|3[0-1])\.(0[1-9]|1[0-2])\.([0-9]{4})$'
    date_format = '%d.%m.%Y'

    claim_json_with_converted_types = copy(claim_json)

    for key, value in claim_json.items():
        if type(value) == str:

            # Replacing missing value with None.
            if value.strip() == "":
                claim_json_with_converted_types[key] = None

            # Converting strings matching date format to datetime.datetime
            elif re.match(date_pattern, value):
                claim_json_with_converted_types[key] = datetime.strptime(value, date_format).replace(tzinfo=None)

    return claim_json_with_converted_types


def convert_json(json_str) -> list[dict] | None:
    """
    Converter aimed to ingest properly 'contracts' column
    of initial dataset from CSV file.

    :param json_str: JSON in 'contracts' column field.
    :return: Properly formatted JSON with converted types.
    """

    if not json_str.strip():
        return None

    try:
        json_data = json.loads(json_str)

        # If 'contracts' field contains only one contract,
        # wrapping it in list for general consistency.
        if type(json_data) == dict:
            json_data = [json_data]

        # Data types conversion for each claim.
        return [convert_claim_json(claim_json) for claim_json in json_data]
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return None


def convert_datetime(datetime_str) -> datetime | None:
    """
    Converter aimed to ingest properly 'application_date' column.

    :param datetime_str: ISO-formatted datetime string.
    :return: datetime64[ns] value.
    """
    if not datetime_str.strip():
        return None

    try:
        datetime_data = datetime.fromisoformat(datetime_str).replace(tzinfo=None)
        return datetime_data
    except Exception as e:
        print(f"Error parsing date: {e}")
        return None


def load_data(filepath: str) -> pd.DataFrame:
    """
    Loading initial dataset with proper types conversion
    to pandas Data Frame.

    :param filepath: Source CSV filepath.
    :return: pd.DataFrame.
    """
    df = pd.read_csv(
        filepath,
        dtype={
            'id': int
        },
        converters={
            'contracts': convert_json,
            'application_date': convert_datetime
        }
    )
    print(f"Total number of rows loaded: {len(df)}")
    print(f"DF columns:\n {df.dtypes}")
    return df
