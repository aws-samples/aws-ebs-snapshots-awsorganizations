## GetSnapshotDetailsAllAccountsOU

## ** Describe GetSnapshotDetailsAllAccountsOU here **

> This is a python script to help you get the list of Snapshots and their details for given region. This script is useful to find the waste across whole OU in terms of snapshots. It provides you details on snashots such as its associated volume, its size, Age of snapshot (Time when it was created), most relavant tag info (Owner and Team). This is very useful for quick investigation of snapshots that can be cleaned and help you to save the cost.

> As added features, this script can let you run this against single account as well as all  accounts of OU. You need to provide IAM role which script can assume in every accounts of OU to able to gather info on snapshot. If you don't provide the role (Optional), script will run only against the account that is configured in your aws config (credentials)

> Script logs run time messages are logged into file called **GetSnapshotDetailsAllAccountsOU.log**. You can check the progress of the script over there while script could be running

> You can use this python script to run it once or you can make lambda function that can be scheduled to run daily via CloudWatch scheduler. Destination can be another S3 bucket.

## Documentation or Example usage:

> ** python3 GetSnapshotDetailsAllAccountsOU.py --file output.csv  --region us-east-1**

> ** python3 GetSnapshotDetailsAllAccountsOU.py --file output.csv  --region us-east-1--account 123456789012 --role OrgPowerUserRole **

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
