import boto3
import json
import boto3.session

def lambda_handler(event, context):

    # update the accountList if any new Account No. needs to be added
    accountList = ["123456789012", "987654321012", "345671230987"]
    
    accountId = event['accountId']
    newContactInfo = event['ContactInformation']
    
    if accountId != "":
        accountList = [accountId]

    for acc in accountList:
        
        try:
            stsClient = boto3.client('sts')

            print(f"Assuming role in {acc} account")
            stsResponse = stsClient.assume_role(
                RoleArn=f'arn:aws:iam::{acc}:role/AccountManager-ExecutionRole',
                RoleSessionName='AccountManager-ExecutionRole',
                DurationSeconds=900
            )

            accessKeyId = stsResponse['Credentials']['AccessKeyId']
            secretAccessKey = stsResponse['Credentials']['SecretAccessKey']
            sessionToken = stsResponse['Credentials']['SessionToken']

            sessionClient = boto3.session.Session(
                aws_access_key_id=accessKeyId, aws_secret_access_key=secretAccessKey, aws_session_token=sessionToken, region_name='us-east-1')
            account = sessionClient.client('account')
            
            update_contact_information(event, account, acc)
                        
        except BaseException as err:
            print(f"Exception raised for {acc} account")
            raise
        
    return {
        'statusCode': 200,
        'body': json.dumps('Successfully updated the contact details in account and s3 bucket')
    }

def update_contact_information(event, account, acc):
    newContactInfo = event['ContactInformation']
    try:
        print(f"Getting contact information from {acc} account")
        sessionResponse = account.get_contact_information()

        # keeping backup in S3
        put_contact_backup(sessionResponse, acc)

    except BaseException as err:
        print(f"Exception raised for {acc} account")
        raise
    else:    
        print(f"Updating contact information in {acc} account")
        account.put_contact_information(
            ContactInformation=newContactInfo
        )
        print("Update successful")

def put_contact_backup(sessionResponse, acc):
    try:
        s3 = boto3.resource('s3')
        bucket = s3.Bucket('backup-s3-bucket')
        contactInfo = json.dumps(sessionResponse['ContactInformation'])
        print(f"Contact Information:{contactInfo}")

        print("Uploading security contact information to S3")
        s3.Object('backup-s3-bucket', f'primary-contact-{acc}.json').put(Body=contactInfo)
        print("Upload successful")

    except BaseException as err:
        #print(f"Exception raised for {acc} account")
        raise
