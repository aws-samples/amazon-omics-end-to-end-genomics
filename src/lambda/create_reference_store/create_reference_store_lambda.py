from crhelper import CfnResource
import logging
import boto3
from botocore.exceptions import ClientError
import os 

logger = logging.getLogger(__name__)
# Initialise the helper, all inputs are optional, this example shows the defaults
helper = CfnResource(json_logging=False, log_level='DEBUG', boto_level='CRITICAL', polling_interval=1)

# Use omics model from lambda layer
os.environ['AWS_DATA_PATH'] = '/opt/models'

# Initiate client
try:
    print("Attempt to initiate client")
    omics_session = boto3.Session()
    omics_client = omics_session.client('omics')
    print("Attempt to initiate client complete")
except Exception as e:
    helper.init_failure(e)


@helper.create
def create(event, context):
    logger.info("Got Create")
    create_omics_reference_store(event, context)


@helper.update
def update(event, context):
    logger.info("Got Update")
    create_omics_reference_store(event, context)


@helper.delete
def delete(event, context):
    logger.info("Got Delete")
    pass
    # Delete never returns anything. Should not fail if the underlying resources are already deleted. Desired state.

def handler(event, context):
    helper(event, context)

def create_omics_reference_store(event, context):
    reference_store_name = event['ResourceProperties']['ReferenceStoreName']
    try:
        print(f"Attempt to create reference store: {reference_store_name}")
        response = omics_client.create_reference_store(
            name=reference_store_name
            )
    except ClientError as e:
        raise Exception( "boto3 client error : " + e.__str__())
    except Exception as e:
       raise Exception( "Unexpected error : " +    e.__str__())
    logger.info(response)
    helper.Data.update({"ReferenceStoreArn": response['arn']})
    helper.Data.update({"ReferenceStoreId": response['id']})
    return True 

