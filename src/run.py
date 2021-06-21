import sys
import csv
from time import sleep
from libs.role import create_trend_cross_account_role
from libs.ws import create_aws_connector, get_aws_external_id

TREND_ASSUME_ROLE_NAME = "Workload_Security_Role_Cross"
TREND_ASSUME_ROLE_POLICY_NAME = "Workload_Security_Policy_Cross"
TREND_AWS_ACCOUNT_ID = "147995105371"
AWS_CROSS_ACCOUNT_ROLE_NAME = "OrganizationAccountAccessRole"
ACCOUNTS_CSV_FILENAME = "accounts.csv"
SLEEP_TIME = 10


def _get_role_name_policy_name():
    if len(sys.argv) == 1:
        return TREND_ASSUME_ROLE_NAME, TREND_ASSUME_ROLE_POLICY_NAME

    elif len(sys.argv) == 2:
        role_name = sys.argv[1]
        return role_name, TREND_ASSUME_ROLE_POLICY_NAME

    elif len(sys.argv) > 2:
        role_name = sys.argv[1]
        policy_name = sys.argv[2]
        return role_name, policy_name


def get_account_number_display_name_map():
    account_number_display_name_map = {}

    with open(ACCOUNTS_CSV_FILENAME, "r") as f:
        csv_entries = csv.DictReader(f)

        for entry in csv_entries:
            account_number = entry["AccountNumber"]
            display_name = entry["DisplayName"]
            account_number_display_name_map[account_number] = display_name

    return account_number_display_name_map


def main():
    account_number_display_name_map = get_account_number_display_name_map()
    account_numbers = list(account_number_display_name_map.keys())
    trend_external_id = get_aws_external_id()
    trend_assume_role_name, trend_assume_role_policy_name = _get_role_name_policy_name()

    role_details = create_trend_cross_account_role(
        TREND_AWS_ACCOUNT_ID,
        trend_external_id,
        AWS_CROSS_ACCOUNT_ROLE_NAME,
        account_numbers,
        trend_assume_role_name,
        trend_assume_role_policy_name,
    )

    print(f"Sleeping for {SLEEP_TIME} seconds to enable AWS policies to take effect...")
    sleep(SLEEP_TIME)

    for details in role_details:
        aws_account_id = details["aws_accont_id"]
        cross_account_role_arn = details["cross_account_role_arn"]
        account_alias = account_number_display_name_map[aws_account_id]
        create_aws_connector(aws_account_id, account_alias, cross_account_role_arn)


if __name__ == "__main__":
    main()
