import os
import sys
import warnings
import deepsecurity
from deepsecurity.rest import ApiException


if not sys.warnoptions:
    warnings.simplefilter("ignore")

WS_API_KEY = os.environ["WS_KEY"]
DS_URL = os.environ.get("DS_URL", "https://cloudone.trendmicro.com/api")
API_VERSON = os.environ.get("WS_API_VERSION", "v1")
configuration = deepsecurity.Configuration()

configuration.host = DS_URL
configuration.api_key["api-secret-key"] = WS_API_KEY


def get_aws_external_id():
    api_instance = deepsecurity.AWSConnectorSettingsApi(
        deepsecurity.ApiClient(configuration)
    )

    try:
        api_response = api_instance.list_aws_connector_settings(API_VERSON)
        external_id = api_response.external_id

    except ApiException as e:
        print(
            "An exception occurred when calling AWSConnectorSettingsApi.list_aws_connector_settings: %s\n"
            % e
        )

    return external_id


def create_aws_connector(aws_account_id, display_name, cross_account_role_arn):
    api_instance = deepsecurity.AWSConnectorsApi(deepsecurity.ApiClient(configuration))

    print(
        f"Creating AWS Connector for '{display_name}' ({aws_account_id}). This may take a minute or two..."
    )
    aws_connector = deepsecurity.AWSConnector(
        display_name=display_name,
        cross_account_role_arn=cross_account_role_arn,
    )

    try:
        api_instance.create_aws_connector(aws_connector, API_VERSON)
        print("Done")

    except ApiException as e:
        print(
            "An exception occurred when calling AWSConnectorsApi.create_aws_connector: %s\n"
            % e
        )
