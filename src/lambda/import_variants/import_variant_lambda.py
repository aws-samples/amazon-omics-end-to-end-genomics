import boto3
from botocore.exceptions import ClientError
import os 


# Use omics model from lambda layer
os.environ['AWS_DATA_PATH'] = '/opt/models'

# Initiate client
try:
    print("Attempt to initiate client")
    omics_session = boto3.Session()
    omics_client = omics_session.client('omics')
    print("Attempt to initiate client complete")
except Exception as e:
    raise e

def handler(event, context):
    variant_store_name = event['VariantStoreName']
    role_arn = event['OmicsImportVariantRoleArn']
    variant_items = [{
        "source": event['VcfS3Uri']
    }]
    try:
        print("Attempt to start variant import job")
        response = omics_client.start_variant_import_job(
            destinationName=variant_store_name,
            roleArn=role_arn,
            items=variant_items
            )
    except ClientError as e:
        raise Exception( "boto3 client error : " + e.__str__())
    except Exception as e:
       raise Exception( "Unexpected error : " +    e.__str__())
    print(response)
    return {"VariantImportJobId": response['jobId']}