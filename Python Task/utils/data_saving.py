import pandas as pd


def save_processed_dataset(
        df: pd.DataFrame,
        filepath: str
) -> None:
    df.to_csv(filepath)
