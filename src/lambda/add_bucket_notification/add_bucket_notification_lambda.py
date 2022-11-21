from crhelper import CfnResource
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
# Initialise the helper, all inputs are optional, this example shows the defaults
helper = CfnResource(json_logging=False, log_level='DEBUG', boto_level='CRITICAL', polling_interval=1)

# Initiate client
try:
    print("Attempt to initiate client")
    s3 = boto3.resource('s3')
    print("Attempt to initiate client complete")
except Exception as e:
    raise e

@helper.create
def create(event, context):
    logger.info("Got Create")
    put_bucket_notification(event, context)


@helper.update
def update(event, context):
    logger.info("Got Update")
    put_bucket_notification(event, context)


@helper.delete
def delete(event, context):
    logger.info("Got Delete")
    pass
    # Delete never returns anything. Should not fail if the underlying resources are already deleted. Desired state.

def handler(event, context):
    helper(event, context)

def put_bucket_notification(event, context):
    bucket_name = event['ResourceProperties']['BucketName']
    prefix = event['ResourceProperties']['Prefix']
    lambda_function_arn = event['ResourceProperties']['LambdaFunctionArn']
    try:
        print("Attempt to update bucket configuration")
        bucket_notification = s3.BucketNotification(bucket_name)
        response = bucket_notification.put(
            NotificationConfiguration={
                'LambdaFunctionConfigurations': [
                {
                    'Id': 'ObjectCreatedStartsWithPrefix',
                    'LambdaFunctionArn': lambda_function_arn,
                    'Events': [
                        's3:ObjectCreated:*'
                    ],
                    'Filter': {
                        'Key': {
                            'FilterRules': [
                                {
                                    'Name': 'prefix',
                                    'Value': prefix
                                },
                            ]
                        }
                    }
                },
            ]
        },
        )
    except ClientError as e:
        raise Exception( "boto3 client error : " + e.__str__())
    except Exception as e:
       raise Exception( "Unexpected error : " +    e.__str__())
    print(response)