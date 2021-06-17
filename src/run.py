import csv
from time import sleep
from libs.role import create_trend_cross_account_role
from libs.ws import create_aws_connector, get_aws_external_id


TREND_AWS_ACCOUNT_ID = "147995105371"
AWS_CROSS_ACCOUNT_ROLE_NAME = "OrganizationAccountAccessRole"
ACCOUNTS_CSV_FILENAME = "accounts.csv"
SLEEP_TIME = 5


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

    role_details = create_trend_cross_account_role(
        TREND_AWS_ACCOUNT_ID,
        trend_external_id,
        AWS_CROSS_ACCOUNT_ROLE_NAME,
        account_numbers,
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
