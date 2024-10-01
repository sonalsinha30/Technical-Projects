import boto3,datetime,os
import json,urllib3,csv
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def lambda_handler(event, context):
    
    try:
                
        userUrl = 'https://sample.com/api/users'
        userresp = http.request('GET', userUrl, headers={"Authorization": "dfhwehri63dfsdfdhfjd", "Accept": "application/json", "Content-Type": "application/json"})
        usersResponse = userresp.data.decode('utf-8')
        userList = json.loads(usersResponse)
        
        ### SAVE THE USER LIST INTO CSV ###
            
        filepath = '/tmp/UsersList.csv'
        # open the file for writing
        data_file = open(filepath, 'w')
            
        # create the csv writer object
        csv_writer = csv.writer(data_file)
            
        # Counter variable used for writing headers to the CSV file
        count = 0
            
        for users in userList:
            if count == 0:
             
                # Writing headers of CSV file
                header = users.keys()
                csv_writer.writerow(header)
            count += 1
             
            # Writing data of CSV file
            csv_writer.writerow(users.values())

        data_file.close()
            
            
        ### FORM THE MAIL BODY AND ATTACHMENT ###
            
        # The email body for recipients with non-HTML email clients.
        BODY_TEXT = "Hello,\r\nPlease find the attached list of users."
        # The HTML body of the email.
        BODY_HTML = """\
        <html>
        <head></head>
        <body>
        <p>Hello,</p>
        <p>Please find the attached list of users.</p>
        </body>
        </html>
        """
        CHARSET = "utf-8"
            
        sesClient = boto3.client('sesv2')
        msg = MIMEMultipart('mixed')
        # Add subject, from and to lines.
        msg['Subject'] = 'List of Users' 
        msg['To'] = 'test@abc.com'
            
        msg_body = MIMEMultipart('alternative')
        textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
        htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)
        # Add the text and HTML parts to the child container.
        msg_body.attach(textpart)
        msg_body.attach(htmlpart)
            
        # Define the attachment part and encode it using MIMEApplication.
        att = MIMEApplication(open(filepath, 'rb').read())
        att.add_header('Content-Disposition','attachment',filename='UsersList.csv')
            
        # Attach the multipart/alternative child container to the multipart/mixed parent container.
        msg.attach(msg_body)
        # Add the attachment to the parent container.
        msg.attach(att)
        print('Report Generated')
            
        ### USE SES TO SEND RAW MAIL WITH ATTACHMENT  ###
                    
        sesClient = boto3.client('sesv2') 
        sesResponse = sesClient.send_email(
            FromEmailAddress="no-reply@abc.com",
            FromEmailAddressIdentityArn="arn:aws:ses:us-east-2:123456789012:identity/test.com",
            Content={
                'Raw': {
                    'Data':msg.as_string()
                }
            }
        )
        
    ### RAISE EXCEPTION IF REPORT GENERATION FAILED  ###
    
    except BaseException as err:
        print("Exception raised")
        raise
