import pandas as pd
import datetime
import json

def convert_json(json_str) -> list[dict] | None:
    if not json_str.strip():
        return None
    try:
        json_data = json.loads(json_str)
        if type(json_data) == dict:
            return [json_data]
        return json_data
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return None

def convert_datetime(datetime_str) -> datetime.datetime | None:
    if not datetime_str.strip():
        return None
    try:
        datetime_data = datetime.datetime.fromisoformat(datetime_str)
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

