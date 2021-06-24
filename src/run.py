import os
import sys
import csv
from time import sleep
from libs.role import create_trend_cross_account_role
from libs.ws import create_aws_connector, get_aws_external_id


WORKLOAD_SECURITY_URL = "https://cloudone.trendmicro.com/api"
DS_URL = os.environ.get("DS_URL", WORKLOAD_SECURITY_URL)
WS_HOST = True if DS_URL == WORKLOAD_SECURITY_URL else False
TREND_ASSUME_ROLE_NAME = "Workload_Security_Role_Cross"
TREND_ASSUME_ROLE_POLICY_NAME = "Workload_Security_Policy_Cross"
TREND_AWS_ACCOUNT_ID = "147995105371"
AWS_CROSS_ACCOUNT_ROLE_NAME = "OrganizationAccountAccessRole"
ACCOUNTS_CSV_FILENAME = "accounts.csv"
SLEEP_TIME = 10


def get_account_id_details_map():
    account_id_details_map = {}

    with open(ACCOUNTS_CSV_FILENAME, "r") as f:
        csv_entries = csv.DictReader(f)

        for entry in csv_entries:
            account_id = entry["AccountId"]

            # Error out if no role name is provided for DS.
            # When run for WS, the role gets populated dynamically.
            ds_cross_account_role = entry.get("CrossAccountRoleArn", '')
            if not WS_HOST and not ds_cross_account_role:
                sys.exit('Error: The CSV file requies the "CrossAccountRoleArn" column.')

            account_id_details_map[account_id] = {
                'DisplayName': entry["DisplayName"],
                'CrossAccountRoleArn': ds_cross_account_role,
            }

    return account_id_details_map


def main():
    # Read the CSV file into a dict
    account_id_details_map = get_account_id_details_map()

    # If using Workload Security, create a cross-account role in each account.
    if WS_HOST:
        trend_external_id = get_aws_external_id()

        for account_id in account_id_details_map:
            cross_account_role_arn = create_trend_cross_account_role(
                TREND_AWS_ACCOUNT_ID,
                trend_external_id,
                TREND_ASSUME_ROLE_NAME,
                TREND_ASSUME_ROLE_POLICY_NAME,
                AWS_CROSS_ACCOUNT_ROLE_NAME,
                account_id,
            )

            account_id_details_map[account_id]['CrossAccountRoleArn'] = cross_account_role_arn

        print(f"Sleeping for {SLEEP_TIME} seconds to enable AWS policies to take effect...")
        sleep(SLEEP_TIME)

    print('Rolling out the AWS connectors...')
    for account_id, account_details in account_id_details_map.items():
        cross_account_role_arn = account_details["CrossAccountRoleArn"]
        display_name = account_details['DisplayName']
        create_aws_connector(account_id, display_name, cross_account_role_arn)


if __name__ == "__main__":
    main()
