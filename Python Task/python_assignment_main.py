import pandas as pd
import datetime
import json
from utils.data_loading import load_data

RAW_DATA_DIR = "./Python Task/data/data.csv"


def calculate_tot_claim_cnt_l180_per_id(contract_list: list[dict],
                                        current_date: datetime.datetime) -> int:
    claims_l180 = set()
    for contract in contract_list:
        if contract['claim_date'] is not None:
            if contract['claim_id'] not in claims_l180 and (current_date - contract['claim_date']).days < 180:
                claims_l180.add(contract['claim_id'])

    return len(claims_l180)


def calculate_tot_claim_cnt_l180(df: pd.DataFrame,
                                 feature_column_name: str = 'tot_claim_cnt_l180',
                                 source: str = 'contracts') -> pd.DataFrame:
    """
    Description: number of claims for last 180 days
    Source: contracts
    Key fields: claim_id, claim_date
    Special notes:
    1. In case claim date is null, don't take into consideration such claims.

    :return:
    """
    df[feature_column_name] = df[source].apply(
        lambda x: calculate_tot_claim_cnt_l180_per_id(x, datetime.datetime.now(tz=None)) if x else None
    )
    return df


def calculate_disb_bank_loan_wo_tbc_per_id(contracts_list: list[dict]) -> float:
    not_tbc_claim_banks = ['LIZ', 'LOM', 'MKO', 'SUG', None]

    total_exposure_sum = 0.0
    for contract in contracts_list:
        try:
            if 'bank' in contract.keys():
                if contract['contract_date'] is not None and contract['bank'] not in not_tbc_claim_banks:
                    contract_loan_summa = contract['loan_summa']
                    if contract_loan_summa is not None:
                        total_exposure_sum += float(contract_loan_summa)
        except Exception as e:
            print(f"Contract processing fails: {e}")
    return total_exposure_sum


def calculate_disb_bank_loan_wo_tbc(df: pd.DataFrame,
                                    feature_column_name: str = 'disb_bank_loan_wo_tbc',
                                    source: str = 'contracts') -> pd.DataFrame:
    """
    Description: Sum of expose of loans without TBC loans. Exposure means here field ""loan_summa"".
    Source: contracts
    Key fields: bank, loan_summa, contract_date
    Special notes:
    1. Consider only loans where field ""bank"" is not in ['LIZ', 'LOM', 'MKO', 'SUG', null].
    2. Disbursed loans means loans where contract_date is not null

    :return: pd.DataFrame with feature column added
    """
    df[feature_column_name] = df[source].apply(lambda x: calculate_disb_bank_loan_wo_tbc_per_id(x) if x else None)
    return df


def calculate_day_sinlastloan_per_id(contract_list: list[dict],
                                     application_date: datetime.datetime) -> int | None:
    last_claim_date = datetime.datetime.min
    for contract in contract_list:
        if contract['summa'] is not None:
            claim_date = contract['claim_date']
            if claim_date is not None:
                last_claim_date = max(last_claim_date, claim_date)

    if last_claim_date == datetime.datetime.min:
        return None
    return (application_date - last_claim_date).days


def calculate_day_sinlastloan(df: pd.DataFrame,
                              feature_column_name: str = 'day_sinlastloan',
                              source: str = 'contracts') -> pd.DataFrame:
    """
    Description: Number of days since last loan.
    Source: contracts
    Key fields: contract_date, summa
    Special notes:
    1. Take last loan of client where summa is not null and calculate
       number of days from contract_date of this loan to application date.

    :return:
    """
    df[feature_column_name] = df.apply(
        lambda x: calculate_day_sinlastloan_per_id(x[source], x['application_date']) if x[source] else None,
        axis=1
    )
    return df


if __name__ == "__main__":
    raw_df = load_data(RAW_DATA_DIR)
    raw_df = calculate_disb_bank_loan_wo_tbc(raw_df)
    raw_df = calculate_day_sinlastloan(raw_df)
    raw_df = calculate_tot_claim_cnt_l180(raw_df)
    print(raw_df.head(10))
    print(raw_df.dtypes)
