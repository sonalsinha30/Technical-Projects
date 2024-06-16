import boto3,json

def lambda_handler(event, context):
    
        #fetch accountID, region and log group name
        logGroupName = event['detail']['requestParameters']['logGroupName']

        # set retentionPeriod variable as per preferred no. of days
        retentionPeriod = 7

        cwClient = boto3.client('logs')
        cwLogGroups = cwClient.describe_log_groups(logGroupNamePrefix=logGroupName)
        
        #extract logGroups if returned in dict
        if 'logGroups' in cwLogGroups:
            logGroups = cwLogGroups['logGroups']
        
        #put retention policy if retentionInDays in not returned i.e. Never Expire        
        for logGroup in logGroups:
            if 'retentionInDays' not in logGroup:                
                print(f"Changing retention period to {retentionPeriod} days for {logGroupName} log group")
                response = cwClient.put_retention_policy(logGroupName=logGroupName,retentionInDays=retentionPeriod)
