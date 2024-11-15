import pandas as pd
import datetime
from utils.data_loading import load_data
from utils.add_feature import add_row_wise_feature

RAW_DATA_DIR = "./Python Task/data/input_data/data.csv"


def calculate_tot_claim_cnt_l180_per_id(
        contract_list: list[dict] | None,
        current_date: datetime.datetime
) -> int:
    """
    Description: number of claims for last 180 days
    Source: contracts
    Key fields: claim_id, claim_date

    Special notes:
    1. In case claim date is null, don't take into consideration such claims.

    :param contract_list: List of claim JSONs for current id.
    :param current_date: Last date, i.e. end of desired 180 days period.
    :return: Number of claims with `claim_date` not earlier than 180 days before `current_date`.
             -3 in case, when no such claims were found.
    """
    if contract_list is None:
        return -3

    claims_l180 = set()

    for contract in contract_list:
        if (
                contract['claim_date'] is not None and
                contract['claim_id'] not in claims_l180 and
                (current_date - contract['claim_date']).days < 180
        ):
            claims_l180.add(contract['claim_id'])

    if not claims_l180:
        return -3

    return len(claims_l180)


def calculate_disb_bank_loan_wo_tbc_per_id(
        contracts_list: list[dict] | None
) -> float:
    """
    Description: Sum of exposue of loans without TBC loans. Exposure means here field ""loan_summa"".
    Source: contracts
    Key fields: bank, loan_summa, contract_date

    Special notes:
    1. Consider only loans where field ""bank"" is not in ['LIZ', 'LOM', 'MKO', 'SUG', null].
    2. Disbursed loans means loans where contract_date is not null"

    :param contracts_list: List of claim JSONs for current id.
    :return: Total sum of `loan_summa` of claims without TBC.
             -3 in case of no claims at all.
             -1 in case of no filled `loan_summa` for non-TBC claims were provided.
    """
    if not contracts_list:
        return -3

    not_tbc_claim_banks = ['LIZ', 'LOM', 'MKO', 'SUG', None]
    total_exposure_sum_not_tbc = 0.0
    total_exposure_num_not_tbc = 0

    for contract in contracts_list:
        if (
                'bank' in contract.keys() and
                contract['contract_date'] is not None and
                contract['loan_summa'] is not None and
                contract['bank'] not in not_tbc_claim_banks
        ):
            total_exposure_sum_not_tbc += contract['loan_summa']
            total_exposure_num_not_tbc += 1

    if total_exposure_num_not_tbc == 0:
        return -1

    return total_exposure_sum_not_tbc


def calculate_day_sinlastloan_per_id(
        contract_list: list[dict] | None,
        application_date: datetime.datetime
) -> int | None:
    """
    Description: Number of days since last loan.
    Source: contracts
    Key fields: contract_date, summa

    Special notes:
    1. Take last loan of client where summa is not null and calculate number of
       days from contract_date of this loan to application date.

    :param contract_list: List of claim JSONs for current id.
    :param application_date: Application date for the current id.
    :return: Number of days between last loan and application date.
             -3 in case of no claims at all.
             -1 in case of no filled `summa` were provided.
    """

    if not contract_list:
        return -3

    last_claim_date = datetime.datetime.min
    for contract in contract_list:
        if (
                contract['summa'] is not None and
                contract['claim_date'] is not None
        ):
            last_claim_date = max(last_claim_date, contract['claim_date'])

    if last_claim_date == datetime.datetime.min:
        return -1

    return (application_date - last_claim_date).days


if __name__ == "__main__":
    contracts_df = load_data(RAW_DATA_DIR)
    contracts_df = add_row_wise_feature(
        contracts_df,
        'disb_bank_loan_wo_tbc',
        'contracts',
        calculate_disb_bank_loan_wo_tbc_per_id
    )
    contracts_df = add_row_wise_feature(
        contracts_df,
        'tot_claim_cnt_l180',
        'contracts',
        calculate_tot_claim_cnt_l180_per_id,
        datetime.datetime.now()
    )
    contracts_df = add_row_wise_feature(
        contracts_df,
        'day_sinlastloan',
        'contracts',
        calculate_day_sinlastloan_per_id,
        contracts_df['application_date'].iloc[0],
        axis=1
    )

    print(contracts_df.head(10))
    print(contracts_df.dtypes)
