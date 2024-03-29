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
    omics_session = boto3.Session()
    omics_client = omics_session.client('omics')
    print("Attempt to initiate client complete")
except Exception as e:
    helper.init_failure(e)


@helper.create
def create(event, context):
    logger.info("Got Create")
    import_reference(event, context)


@helper.update
def update(event, context):
    logger.info("Got Update")
    import_reference(event, context)


@helper.delete
def delete(event, context):
    logger.info("Got Delete")
    return "delete"
    # Delete never returns anything. Should not fail if the underlying resources are already deleted. Desired state.

@helper.poll_create
def poll_create(event, context):
    logger.info("Got Create poll")
    return check_reference_import_status(event, context)


@helper.poll_update
def poll_update(event, context):
    logger.info("Got Update poll")
    return check_reference_import_status(event, context)


@helper.poll_delete
def poll_delete(event, context):
    logger.info("Got Delete poll")
    return "delete poll"

def handler(event, context):
    helper(event, context)

def import_reference(event, context):
    reference_store_id = event['ResourceProperties']['ReferenceStoreId']
    omics_import_role_arn = event['ResourceProperties']['OmicsImportReferenceRoleArn']
    reference_source_s3_uri = event['ResourceProperties']['ReferenceSourceS3Uri']
    reference_name = event['ResourceProperties']['ReferenceName']
    try:
        print(f"Attempt to import reference: {reference_source_s3_uri} to store: {reference_store_id}")
        response = omics_client.start_reference_import_job(
            referenceStoreId=reference_store_id,
            roleArn=omics_import_role_arn,
            sources=[{'sourceFile': reference_source_s3_uri, 'name': reference_name}]
            )
    except ClientError as e:
        raise Exception( "boto3 client error : " + e.__str__())
    except Exception as e:
       raise Exception( "Unexpected error : " +    e.__str__())
    logger.info(response)
    helper.Data.update({"ReferenceImportJobId": response['id']})
    helper.Data.update({"ReferenceStoreId": response['referenceStoreId']})
    return True

def get_reference_arn_id(reference_store_id, reference_name):
    try:
        response = omics_client.list_references(
            referenceStoreId=reference_store_id, 
            filter={'name': reference_name}
            )
    except ClientError as e:
        raise Exception( "boto3 client error : " + e.__str__())
    except Exception as e:
       raise Exception( "Unexpected error : " +    e.__str__())
    return response['references'][0]['arn'], response['references'][0]['id']

def check_reference_import_status(event, context):
    reference_store_id = helper.Data.get("ReferenceStoreId")
    reference_import_job_id = helper.Data.get("ReferenceImportJobId")

    try:
        response = omics_client.get_reference_import_job(
            id=reference_import_job_id, 
            referenceStoreId=reference_store_id
            )
    except ClientError as e:
        raise Exception( "boto3 client error : " + e.__str__())
    except Exception as e:
       raise Exception( "Unexpected error : " +    e.__str__())
    status = response['status']
    
    if status in ['SUBMITTED', 'IN_PROGRESS', 'RUNNING']:
        logger.info(status)
        return None
    else:
        if status in ['READY', 'ACTIVE', 'COMPLETED']:
            logger.info(status)
            _arn, _id = get_reference_arn_id(
                reference_store_id, 
                event['ResourceProperties']['ReferenceName']
                )
            helper.Data.update({"Arn": _arn})
            helper.Data.update({"Id": _id})
            return True
        else:
            msg = f"Reference store: {reference_store_id} has status {status}, exiting"
            logger.info(msg)
            raise ValueError(msg)

