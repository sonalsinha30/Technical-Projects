import boto3,json,boto3.session,time

def lambda_handler(event, context):
    
        #fetch accountID, region and log group name from cross account event triggered using event bus
        accountId = event['account']
        region_name = event['region']
        logGroupName = event['detail']['requestParameters']['logGroupName']
        
        #set retention period for prod and non-prod accounts
        prodAccounts = ['123456789']
        nonprodAccounts = ['987654321']

        # set retentionPeriod variable as oer preferred no. of days
        if accountId in prodAccounts:
            retentionPeriod = 14
        else:
            retentionPeriod = 7
        
        #generate temporary credentials to assume cross account role (assuming that the role CW-ExecutionRole is already present in the traget account)
        stsClient = boto3.client('sts')
        stsResponse = stsClient.assume_role( 
            RoleArn=f'arn:aws:iam::{accountId}:role/CW-ExecutionRole', 
            RoleSessionName='CW-ExecutionRole', 
            DurationSeconds=900 
        ) 
            
        accessKeyId = stsResponse['Credentials']['AccessKeyId'] 
        secretAccessKey = stsResponse['Credentials']['SecretAccessKey'] 
        sessionToken = stsResponse['Credentials']['SessionToken']
        
        #assume cross account role to describe the log group returned in event    
        sessionClient = boto3.session.Session(aws_access_key_id=accessKeyId, aws_secret_access_key=secretAccessKey, aws_session_token=sessionToken,region_name=region_name) 
        cwClient = sessionClient.client('logs', region_name=region_name)
        time.sleep(30)
        cwLogGroups = cwClient.describe_log_groups(logGroupNamePrefix=logGroupName)
        
        #extract logGroups if returned in dict
        if 'logGroups' in cwLogGroups:
            logGroups = cwLogGroups['logGroups']
        
        #put retention policy if retentionInDays in not returned i.e. Never Expire        
        for logGroup in logGroups:
            if 'retentionInDays' not in logGroup:
                print(f"Assuming role in {region_name} region in {accountId} account")
                print(f"Changing retention period to {retentionPeriod} days for {logGroupName} log group")
                response = cwClient.put_retention_policy(logGroupName=logGroupName,retentionInDays=retentionPeriod)
