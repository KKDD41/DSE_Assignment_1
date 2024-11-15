import pandas as pd


def add_row_wise_feature(
        df: pd.DataFrame,
        feature_column_name: str,
        source: str,
        func,
        *args,
        **kwargs
) -> pd.DataFrame:
    """
    Function for adding new row-wise feature based on the 'source' column into
    pandas DataFrame.

    :param df: DataFrame in which to add feature.
    :param feature_column_name: Column name for new feature.
    :param source: The column name from which to source data for the function.
    :param func: The function to apply. It should accept the source data as its first argument.
    :param args: Positional arguments to pass to the function after the source data.
    :param kwargs: Keyword arguments to pass to the function.
    :return: The modified DataFrame with the new feature.
    """

    if 'axis' in kwargs and kwargs['axis'] == 1:
        # Apply function row-wise
        df[feature_column_name] = df.apply(
            lambda x: func(x[source], *args, **{k: v for k, v in kwargs.items() if k != 'axis'}),
            axis=1
        )
    else:
        # Apply function element-wise on the specified column
        df[feature_column_name] = df[source].apply(
            lambda x: func(x, *args, **kwargs)
        )

    return df
