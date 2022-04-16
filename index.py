#lambda
import json
import boto3
import uuid


print('loading function')


def trigger_intance(unique_id):
    user_data = '#!bin/bash\ncd /home/ubuntu/auto_download\npython3 file_updater.py '
    user_data += '"'
    user_data += unique_id
    user_data += '"'
    print(user_data)
    key_pair = 'auto-process-instance'
    iam_profile = {'Name': 'auto-file-processor'}
    
    ec2_client = boto3.client('ec2')
    ec2_client.run_instances(ImageId = 'ami-084e80b04f84b2571',InstanceType = 't2.micro',UserData=user_data,MinCount=1,MaxCount=1,KeyName=key_pair,IamInstanceProfile = iam_profile)
    


def lambda_handler(event, context):

    print('event:\n')
    print(event)
    
    text_ipt = event['text_input']
    object_name = event['ipt_file_name']

    
    s3_client = boto3.client('s3')
    bucket_name = 'file-upload-input-bucket-praveen'
    table_name = 'Dynamo_api-lambda-db'
    expiration = 300

    upd_details = s3_client.generate_presigned_post(bucket_name, object_name, ExpiresIn=expiration)
    
    print('u:',upd_details)

    
    dynamo_db_client = boto3.client('dynamodb')
    
    new_item = {'id':{},'input_text':{},'input_file_path':{}}
    unique_id = str(uuid.uuid4())
    new_item['id']['S'] = unique_id
    new_item['input_text']['S'] = text_ipt
    new_item['input_file_path']['S'] = bucket_name +'/' + object_name
    
    dynamo_db_client.put_item(TableName = table_name, Item= new_item)

    
    http_resp = {}
    http_resp['statusCode'] = 200
    http_resp['headers'] = {}
    http_resp['headers']['Content-Type'] = 'application/json'
    http_resp['body'] = upd_details
    
    print('\n\nhttpres:\n')
    print(http_resp)
    
    trigger_intance(unique_id)
    
    return http_resp
    
    

