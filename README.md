Use this script to generate an on-demand report of all the Amazon EBS Snapshots in their AWS Account or all  Accounts in an AWS Organizations. Using this script, you will be able to gather AWS Account Id, AWS Tags, Snapshot_Id, Volume_Size, Volume_Id, start_time, instance_id, and Description of the Amazon EBS Snapshots.

* You should have the appropriate AWS IAM user or role to run this script in all Accounts in an AWS Organizations.
* You can monitor the progress of the script during its run-time. Check *GetSnapshotDetailsAllAccountsOU.log*** **for additional details.
* To create a scheduled task, use AWS Lambda function and Amazon CloudWatch Event.

Example usage

For AWS Account  ** python3 *GetSnapshotDetailsAllAccountsOU.py --file output.csv --region <_>*

For AWS Organizations ** python3 *GetSnapshotDetailsAllAccountsOU.py --file output.csv --region <_> --account <_> --role <_>*

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
