import constants
import boto3
import sys
from ec2_metadata import ec2_metadata


class File_UPDATER:
    s3_client = boto3.client('s3', region_name=constants.REGION)
    db_client = boto3.client('dynamodb', region_name=constants.REGION)
    ec2_client = boto3.client('ec2', region_name=constants.REGION)
    file_name = ''
    ipt_text = ''
    item_id = sys.argv[1]



    @classmethod
    def download_from_s3(self):
        self.s3_client.download_file(constants.IPT_BUCKET_NAME,self.file_name,self.file_name)

    @classmethod  
    def get_input_text(self):
        new_item = {'id':{}}
        new_item['id']['S'] = self.item_id
        response = self.db_client.get_item(
        TableName='Dynamo_api-lambda-db',
            Key={
                'id': {'S' : self.item_id}
            }
        )
        self.file_name = response['Item']['input_file_path']['S'].split('/')[1]
        self.ipt_text = response['Item']['input_text']['S']
        print(response)
        print(self.file_name)
        print(self.ipt_text)

    @classmethod
    def update_text_of_file(self):
        f = open(self.file_name, "a")
        f.write(':')
        f.write(self.ipt_text)
        f.close()
    
    @classmethod
    def upload_file_to_s3(self):
        self.s3_client.upload_file(self.file_name, constants.OPT_BUCKET_NAME, self.file_name)
    
    @classmethod
    def self_terminate(self):
        instance_id = ec2_metadata.instance_id
        try:
            self.ec2_client.terminate_instances(InstanceIds=[instance_id])
        except Exception as e:
            print(e)
        

if __name__ == "__main__":
    #pass
    File_UPDATER.get_input_text()
    File_UPDATER.download_from_s3()
    File_UPDATER.update_text_of_file()
    File_UPDATER.upload_file_to_s3()
    File_UPDATER.self_terminate()
