import json
import boto3
from botocore.exceptions import ClientError


ROLE_SESSION_NAME = "Workload_Security_Cross_Account_Creation_Session"


TREND_WORKLOAD_SECURITY_POLICY = json.dumps(
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "cloudconnector",
                "Action": [
                    "ec2:DescribeImages",
                    "ec2:DescribeInstances",
                    "ec2:DescribeRegions",
                    "ec2:DescribeSubnets",
                    "ec2:DescribeTags",
                    "ec2:DescribeVpcs",
                    "ec2:DescribeAvailabilityZones",
                    "ec2:DescribeSecurityGroups",
                    "workspaces:DescribeWorkspaces",
                    "workspaces:DescribeWorkspaceDirectories",
                    "workspaces:DescribeWorkspaceBundles",
                    "workspaces:DescribeTags",
                    "iam:ListAccountAliases",
                    "iam:GetRole",
                    "iam:GetRolePolicy",
                ],
                "Effect": "Allow",
                "Resource": "*",
            }
        ],
    }
)


def _get_trend_assume_role_policy(trend_aws_account_id, trend_external_id):
    """Creates cross account policy using customer's unique external ID

    Args:
        trend_aws_account_id:
        trend_external_id:

    Returns:

    """
    print("Generating cross-account policy...")

    assume_role_policy = json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": f"arn:aws:iam::{trend_aws_account_id}:root"},
                    "Action": ["sts:AssumeRole"],
                    "Condition": {
                        "StringEquals": {"sts:ExternalId": trend_external_id}
                    },
                }
            ],
        }
    )

    return assume_role_policy


def _get_child_account_keys(aws_cross_account_role_name, customer_account_id):
    print(f"Asssuming role: {aws_cross_account_role_name}")
    sts = boto3.client("sts")
    response = sts.assume_role(
        RoleSessionName=ROLE_SESSION_NAME,
        RoleArn=f"arn:aws:iam::{customer_account_id}:role/{aws_cross_account_role_name}",
    )

    access_key_id = response["Credentials"]["AccessKeyId"]
    secrect_access_key = response["Credentials"]["SecretAccessKey"]
    session_token = response["Credentials"]["SessionToken"]
    print("Got credentials from assumed role")

    return access_key_id, secrect_access_key, session_token


def _get_role_arn(iam, new_assume_role_name):
    print("Role already exists. Searching for its ARN...")

    paginator = iam.get_paginator("list_roles")
    response_iterator = paginator.paginate()

    for response in response_iterator:
        for role in response["Roles"]:
            if role["RoleName"] == new_assume_role_name:
                role_arn = role["Arn"]
                print(f'Found it: "{role_arn}"')

                return role_arn


def _get_policy_arn(iam, new_assume_role_policy_name):
    print("Policy already exists. Searching for its ARN...")

    paginator = iam.get_paginator("list_policies")
    response_iterator = paginator.paginate()

    for response in response_iterator:
        for policy in response["Policies"]:
            if policy["PolicyName"] == new_assume_role_policy_name:
                policy_arn = policy["Arn"]
                print(f'Found it: "{policy_arn}"')

                return policy_arn


def _create_trend_cross_account_role(
    access_key_id,
    secrect_access_key,
    session_token,
    trend_assume_role_name,
    trend_assume_role_policy_name,
    trend_assume_role_policy,
):
    print(
        f'Creating Trend cross-account role "{trend_assume_role_name}" using retrieved credentials...'
    )

    iam = boto3.client(
        "iam",
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secrect_access_key,
        aws_session_token=session_token,
    )

    try:
        role = iam.create_role(
            RoleName=trend_assume_role_name,
            AssumeRolePolicyDocument=trend_assume_role_policy,
        )

        role_arn = role["Role"]["Arn"]
        print("Done")

    except ClientError as e:
        if e.response["Error"]["Code"] == "EntityAlreadyExists":
            role_arn = _get_role_arn(iam, trend_assume_role_name)

    print(f'Creating cross-account policy "{trend_assume_role_policy_name}"')

    try:
        policy = iam.create_policy(
            PolicyName=trend_assume_role_policy_name,
            PolicyDocument=TREND_WORKLOAD_SECURITY_POLICY,
        )

        policy_arn = policy["Policy"]["Arn"]
        print("Done")

    except ClientError as e:
        if e.response["Error"]["Code"] == "EntityAlreadyExists":
            policy_arn = _get_policy_arn(iam, trend_assume_role_policy_name)

    print(f'Attaching cross-account policy "{trend_assume_role_policy_name}" to role')

    try:
        iam.attach_role_policy(PolicyArn=policy_arn, RoleName=trend_assume_role_name)
        print("Done")

    except ClientError as e:
        if e.response["Error"]["Code"] == "EntityAlreadyExists":
            print("Policy is already attached")

    print("Cross-account role was successfully created")
    return role_arn


def create_trend_cross_account_role(
    trend_aws_account_id,
    trend_external_id,
    aws_cross_account_role_name,
    customer_account_ids,
    trend_assume_role_name,
    trend_assume_role_policy_name,
):
    role_details = []

    trend_assume_role_policy = _get_trend_assume_role_policy(
        trend_aws_account_id, trend_external_id
    )

    for customer_account_id in customer_account_ids:
        print(f"Setting up account {customer_account_id}")

        access_key_id, secrect_access_key, session_token = _get_child_account_keys(
            aws_cross_account_role_name, customer_account_id
        )

        role_arn = _create_trend_cross_account_role(
            access_key_id,
            secrect_access_key,
            session_token,
            trend_assume_role_name,
            trend_assume_role_policy_name,
            trend_assume_role_policy,
        )

        entry = {
            "aws_accont_id": customer_account_id,
            "cross_account_role_arn": role_arn,
        }

        role_details.append(entry)

    return role_details
