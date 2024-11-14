import pandas as pd
from datetime import datetime
import json
from copy import copy
import re

def convert_claim_json(claim_json: dict) -> dict:
    date_pattern = r'^([0-2][0-9]|3[0-1])\.(0[1-9]|1[0-2])\.([0-9]{4})$'
    date_format = '%d.%m.%Y'

    claim_json_with_converted_types = copy(claim_json)
    for key, value in claim_json.items():
        if type(value) == str:
            if value.strip() == "":
                claim_json_with_converted_types[key] = None
            elif re.match(date_pattern, value):
                claim_json_with_converted_types[key] = datetime.strptime(value, date_format).replace(tzinfo=None)

    return claim_json_with_converted_types

def convert_json(json_str) -> list[dict] | None:
    if not json_str.strip():
        return None
    try:
        json_data = json.loads(json_str)
        if type(json_data) == dict:
            json_data = [json_data]

        return [convert_claim_json(claim_json) for claim_json in json_data]
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return None

def convert_datetime(datetime_str) -> datetime | None:
    if not datetime_str.strip():
        return None
    try:
        datetime_data = datetime.fromisoformat(datetime_str).replace(tzinfo=None)
        return datetime_data
    except Exception as e:
        print(f"Error parsing date: {e}")
        return None


def load_data(filepath: str) -> pd.DataFrame:
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
    return df

