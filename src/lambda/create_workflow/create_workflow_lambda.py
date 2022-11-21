from crhelper import CfnResource
import logging
import boto3
from botocore.exceptions import ClientError
import os 
import json

logger = logging.getLogger(__name__)
# Initialise the helper, all inputs are optional, this example shows the defaults
helper = CfnResource(json_logging=False, log_level='DEBUG', boto_level='CRITICAL', polling_interval=1)

# Use omics model from lambda layer
os.environ['AWS_DATA_PATH'] = '/opt/models'

# Initiate client
try:
    print("Attempt to initiate omics client")
    omics_session = boto3.Session()
    omics_client = omics_session.client('omics')
    print("Attempt to initiate client complete")

    print("Attempt to initiate s3 client")
    s3_session = boto3.Session()
    s3_client = s3_session.client('s3')
    print("S3 client initiated")

except Exception as e:
    helper.init_failure(e)


@helper.create
def create(event, context):
    logger.info("Got Create")
    create_workflow(event, context)


@helper.update
def update(event, context):
    logger.info("Got Update")
    create_workflow(event, context)


@helper.delete
def delete(event, context):
    logger.info("Got Delete")
    pass
    # Delete never returns anything. Should not fail if the underlying resources are already deleted. Desired state.

@helper.poll_create
def poll_create(event, context):
    logger.info("Got Create poll")
    return get_create_workflow_status(event, context)


@helper.poll_update
def poll_update(event, context):
    logger.info("Got Update poll")
    return get_create_workflow_status(event, context)


@helper.poll_delete
def poll_delete(event, context):
    logger.info("Got Delete poll")
    return get_create_workflow_status(event, context)


def handler(event, context):
    helper(event, context)

def split_s3_path(s3_path):
    path_parts=s3_path.replace("s3://","").split("/")
    bucket=path_parts.pop(0)
    key="/".join(path_parts)
    return bucket, key

def download_s3_file(s3uri):
    
    _bucket, _key = split_s3_path(s3uri)
    local_file = '/tmp/' + os.path.basename(_key)
    s3_client.download_file(_bucket, _key, local_file)
    return local_file

def create_workflow(event, context):
    workflow_name = event['ResourceProperties']['WorkflowName']
    workflow_description = event['ResourceProperties']['WorkflowDescription']
    workflow_definition_zip = event['ResourceProperties']['WorkflowDefinitionZip']
    workflow_params_json = event['ResourceProperties']['WorkflowParamsJson']
    
    local_wf_params_json = download_s3_file(workflow_params_json)
    
    try:
        wfp = open(local_wf_params_json)
        print(f"Attempt to create workflow with zip: {workflow_definition_zip} and params: {workflow_params_json}")
        response = omics_client.create_workflow(
            name=workflow_name,
            description=workflow_description,
            definitionUri=workflow_definition_zip,
            parameterTemplate=json.load(wfp)
            )
        wfp.close()
    except ClientError as e:
        raise Exception( "boto3 client error : " + e.__str__())
    except Exception as e:
       raise Exception( "Unexpected error : " +    e.__str__())
    logger.info(response)
    helper.Data.update({"WorkflowId": response['id']})
    helper.Data.update({"WorkflowArn": response['arn']})

def get_create_workflow_status(event, context):
    workflow_id = helper.Data.get('WorkflowId')

    try:
        response = omics_client.get_workflow(id=workflow_id)
    except ClientError as e:
        raise Exception( "boto3 client error : " + e.__str__())
    except Exception as e:
       raise Exception( "Unexpected error : " +    e.__str__())
    status = response['status']
    
    if status in ['CREATING', 'UPDATING', 'IN_PROGRESS', 'QUEUED']:
        logger.info(status)
        return None
    else:
        if status in ['READY', 'COMPLETED', 'ACTIVE', 'COMPLETE']:
            logger.info(status)
            helper.Data['Id'] = workflow_id
            return True
        else:
            msg = f"Workflow ID {workflow_id} has status {status}, exiting"
            logger.info(msg)
            raise ValueError(msg)

