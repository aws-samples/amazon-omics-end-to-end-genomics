import boto3
import os

from copy import deepcopy
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Literal

import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Set up for omics model for boto3, only needed while in beta

os.environ['AWS_DATA_PATH'] = '/opt/models'

session = boto3.Session()

omics_client = session.client("omics")

# Define omics service response status types

TASK_TYPE = Literal["GetReadSetImportJob", "GetVariantImportJob", "GetRun"]
READ_SET_IMPORT_STATUS = Literal[
    "CREATED", "SUBMITTED", "RUNNING", "CANCELLING", "FAILED", "DONE", "COMPLETED_WITH_FAILURES"]
GET_RUN_JOB_STATUS = Literal[
    "PENDING", "STARTING", "RUNNING", "STOPPING", "COMPLETED", "DELETED", "CANCELLED", "FAILED"]
GET_VARIANT_IMPORT_JOB_STATUS = Literal[
    "CREATING", "QUEUED", "IN_PROGRESS", "CANCELING", "CANCELED", "COMPLETE", "FAILED"]


# Define data classes


@dataclass
class CheckOmicsWorkflowTaskRequest:
    task_type: TASK_TYPE
    task_params: dict


@dataclass
class CheckOmicsWorkflowTaskResponse(CheckOmicsWorkflowTaskRequest):
    task_status: str = None
    task_response: dict = None


# Converts datetimes to isoformat string
def dates_to_string(response_dict: dict):
    converted_response = deepcopy(response_dict)

    for k, v in response_dict.items():
        if isinstance(v, dict):
            converted_response[k] = dates_to_string(response_dict[k])
        elif isinstance(v, datetime):
            converted_response[k] = response_dict[k].isoformat()
    return converted_response


# Checks if task_status is one of possible values for a terminal state
# Sets value to either COMPLETED, or FAILED if terminal state
def get_terminal_status(task_status) -> str:
    if task_status == 'DONE':
        return "COMPLETED"
    elif task_status in ["CANCELLING", "DELETED", "CANCELLED", "COMPLETED_WITH_FAILURES"]:
        return "FAILED"
    else:
        return task_status


# Make Lambda Function response
def make_response(
        request: CheckOmicsWorkflowTaskRequest,
        task_status: str,
        task_response: dict
) -> CheckOmicsWorkflowTaskResponse:
    del task_response['ResponseMetadata']

    workflow_task_response = CheckOmicsWorkflowTaskResponse(
        task_type=request.task_type,
        task_params=request.task_params,
        task_status=task_status,
        task_response=dates_to_string(task_response)
    )
    return workflow_task_response


# Amazon Omics service calls

def get_read_set_import_job(request: CheckOmicsWorkflowTaskRequest) -> CheckOmicsWorkflowTaskResponse:
    boto3.client('omics')
    response = omics_client.get_read_set_import_job(
        id=request.task_params['id'],
        sequenceStoreId=request.task_params['sequence_store_id']
    )
    logger.info(response)

    workflow_task_response = make_response(
        request=request,
        task_status=get_terminal_status(response['status']),
        task_response=response
    )
    return workflow_task_response


def get_run(request: CheckOmicsWorkflowTaskRequest) -> CheckOmicsWorkflowTaskResponse:
    boto3.client('omics')
    response = omics_client.get_run(
        id=request.task_params['id'],
    )

    logger.info(response)

    workflow_task_response = make_response(
        request=request,
        task_status=get_terminal_status(response['status']),
        task_response=response
    )
    return workflow_task_response


def get_variant_import_job(request: CheckOmicsWorkflowTaskRequest) -> CheckOmicsWorkflowTaskResponse:
    boto3.client('omics')
    response = omics_client.get_variant_import_job(
        jobId=request.task_params['job_id'],
    )

    logger.info(response)

    workflow_task_response = make_response(
        request=request,
        task_status=get_terminal_status(response['status']),
        task_response=response
    )

    return workflow_task_response


# Main lambda handler

def lambda_handler(event: CheckOmicsWorkflowTaskRequest, context):
    logger.info(f"Event Object: {event}")

    request = CheckOmicsWorkflowTaskRequest(**event)

    if request.task_type == "GetReadSetImportJob":
        task_response = get_read_set_import_job(request)
    elif request.task_type == "GetRun":
        task_response = get_run(request)
    elif request.task_type == "GetVariantImportJob":
        task_response = get_variant_import_job(request)
    else:
        task_response = make_response(
            request,
            task_status="FAILED",
            task_response={
                'failure_message': f'The requested task_type: {request.task_type} is not one of: ['
                                   f'GetReadSetImportJob, GetRun, GetVariantImportJob]'}
        )

    return asdict(task_response)