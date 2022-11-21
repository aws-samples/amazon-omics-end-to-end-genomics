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
    _session = boto3.Session()
    code_build_client = _session.client('codebuild')
    print("Attempt to initiate codebuild client complete")
except Exception as e:
    helper.init_failure(e)


@helper.create
def create(event, context):
    logger.info("Got Create")
    start_code_build(event, context)


@helper.update
def update(event, context):
    logger.info("Got Update")
    start_code_build(event, context)


@helper.delete
def delete(event, context):
    logger.info("Got Delete")
    pass
    # Delete never returns anything. Should not fail if the underlying resources are already deleted. Desired state.

@helper.poll_create
def poll_create(event, context):
    logger.info("Got Create poll")
    return check_code_build_status(event, context)


@helper.poll_update
def poll_update(event, context):
    logger.info("Got Update poll")
    return check_code_build_status(event, context)


@helper.poll_delete
def poll_delete(event, context):
    logger.info("Got Delete poll")
    return check_code_build_status(event, context)

def handler(event, context):
    helper(event, context)


def start_code_build(event, context):
    project_name = event['ResourceProperties']['ProjectName']
    
    try:
        print(f"Attempt to start code build project {project_name}")
        response = code_build_client.start_build(
            projectName=project_name
        )
    except ClientError as e:
        raise Exception( "boto3 client error : " + e.__str__())
    except Exception as e:
       raise Exception( "Unexpected error : " +    e.__str__())
    logger.info(response)
    helper.Data.update({"BuildId": response['build']['id']})

def check_code_build_status(event, context):
    build_id = helper.Data.get('BuildId')
    
    try:
        response = code_build_client.batch_get_builds(ids=[build_id])
    except ClientError as e:
        raise Exception( "boto3 client error : " + e.__str__())
    except Exception as e:
       raise Exception( "Unexpected error : " +    e.__str__())
    status = response['builds'][0]['buildStatus']
    
    if status in ['FAILED', 'FAULT', 'STOPPED', 'TIMED_OUT']:
        msg = f"Build ID {build_id} has status {status}, exiting"
        logger.info(msg)
        raise ValueError(msg)
    else:
        if status in ['SUCCEEDED']:
            logger.info(status)
            return True
        else:
            logger.info(f"Build ID status is: {build_id}")
            return None