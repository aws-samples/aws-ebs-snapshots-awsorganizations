#!/usr/bin/env python3
# Name:        GetSnapshotDetailsAllAccountsOU.py
# Purpose:     Get details of EBS snapshots for the current account or all
#              active accounts in an AWS Organization.
# Author:      Parag Nagwekar
# Created:     01/11/2022
# Updated:     11/12/2026 - Removed shell subprocess call (Bandit B602 /
#              Semgrep subprocess-shell-true), hardened cross-account error
#              handling, switched to boto3 paginators.
import argparse
import csv
import logging
import os
import sys

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logging.basicConfig(
    filename="GetSnapshotDetailsAllAccountsOU.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

FIELD_NAMES = [
    "Account", "Snapshot_Id", "Volume_Size", "Volume_Id", "start_time",
    "Owner", "Team", "instance_id", "Description",
]
TAG_FIELDS = {"Owner", "Team", "instance_id"}


def get_all_accounts():
    """Return IDs of all ACTIVE accounts in the AWS Organization."""
    print("Getting all AWS Accounts")
    accounts = []
    paginator = boto3.client("organizations").get_paginator("list_accounts")
    for page in paginator.paginate():
        for account in page["Accounts"]:
            if account["Status"] == "ACTIVE":
                accounts.append(account["Id"])
            else:
                logging.info("Account %s is not active, skipping", account["Id"])
    return accounts


def assume_role(target_account, role):
    """Return temporary credentials for role in target_account, or None on failure."""
    sts = boto3.client("sts")
    try:
        response = sts.assume_role(
            RoleArn=f"arn:aws:iam::{target_account}:role/{role}",
            RoleSessionName="GetSnapshotDetailsCrossAccount",
        )
    except (ClientError, BotoCoreError) as err:
        logging.error("Error assuming role in account %s: %s", target_account, err)
        return None
    return response["Credentials"]


def build_row(account, snap):
    """Build one CSV row from a snapshot record."""
    row = {
        "Account": account,
        "Snapshot_Id": snap["SnapshotId"],
        "Volume_Size": snap["VolumeSize"],
        "Volume_Id": snap["VolumeId"],
        "start_time": snap["StartTime"],
        "Description": snap.get("Description", ""),
    }
    for tag in snap.get("Tags", []):
        if tag["Key"] in TAG_FIELDS:
            row[tag["Key"]] = tag["Value"]
    return row


def get_all_snapshots(account, ec2_client):
    """Return CSV rows for all snapshots owned by account."""
    rows = []
    paginator = ec2_client.get_paginator("describe_snapshots")
    for page in paginator.paginate(OwnerIds=[account], PaginationConfig={"PageSize": 500}):
        snapshots = page["Snapshots"]
        logging.info("Account %s: %d snapshots in page", account, len(snapshots))
        rows.extend(build_row(account, snap) for snap in snapshots)
    return rows


def write_csv(filepath, rows):
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, FIELD_NAMES)
        writer.writeheader()
        writer.writerows(rows)


def main(region, filepath, role):
    current_account = boto3.client("sts").get_caller_identity()["Account"]
    rows = []

    if role:
        accounts = get_all_accounts()
        logging.info("Accounts found: %d", len(accounts))
        for account in accounts:
            logging.info("Processing account %s", account)
            if account == current_account:
                ec2_client = boto3.client("ec2", region_name=region)
            else:
                creds = assume_role(account, role)
                if not creds:
                    logging.warning("Skipping account %s: cannot assume role", account)
                    continue
                ec2_client = boto3.client(
                    "ec2",
                    region_name=region,
                    aws_access_key_id=creds["AccessKeyId"],
                    aws_secret_access_key=creds["SecretAccessKey"],
                    aws_session_token=creds["SessionToken"],
                )
            try:
                rows.extend(get_all_snapshots(account, ec2_client))
            except (ClientError, BotoCoreError) as err:
                logging.error("Failed to list snapshots in account %s: %s", account, err)
    else:
        rows = get_all_snapshots(current_account, boto3.client("ec2", region_name=region))

    write_csv(filepath, rows)
    print(f"Wrote {len(rows)} snapshot records to {filepath}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates a CSV report of EBS snapshots across accounts."
    )
    parser.add_argument("--region", required=True, help="AWS region such as us-east-1")
    parser.add_argument("--file", required=True, help="Path for output CSV file")
    parser.add_argument("--role", required=False,
                        help="IAM role the script can assume in member accounts")
    args = parser.parse_args()

    if os.path.exists(args.file):
        sys.exit(f"Error: output file '{args.file}' already exists.")

    main(args.region, args.file, args.role)
