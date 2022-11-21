import logging
import boto3
from botocore.exceptions import ClientError
import os 

logger = logging.getLogger(__name__)

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
    sequence_store_id = event['SequenceStoreId']
    sample_id = event['SampleId']
    subject_id = event['SubjectId']
    source_file_type = event['FileType']
    source_files = {}
    source1 = event['Read1']
    source_files["source1"] = source1
    if "Read2" in event:
        source2 = event['Read2']
        source_files["source2"] = source2
    reference_arn = event['ReferenceArn']
    role_arn = event['RoleArn']
    source_list = [
        {
            "sourceFiles": source_files,
            "sourceFileType": source_file_type,
            "subjectId": subject_id,
            "sampleId": sample_id,
            "referenceArn": reference_arn
        }
    ]

    try:
        print("Attempt to import read set")
        response = omics_client.start_read_set_import_job(
            sequenceStoreId=sequence_store_id,
            roleArn=role_arn,
            sources=source_list
            )
    except ClientError as e:
        raise Exception( "boto3 client error : " + e.__str__())
    except Exception as e:
       raise Exception( "Unexpected error : " +    e.__str__())
    logger.info(response)
    return {"importReadSetJobId": response['id']}