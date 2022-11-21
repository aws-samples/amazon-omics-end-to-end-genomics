import json
import boto3
import re
import os
import sys
import uuid

print('Loading function - launch Genomics Step Function Workflow')

s3 = boto3.client('s3')

## FASTQ files name should look like 
# mysample_R1.fastq.gz mysample_R2.fastq.gz
# based on regex below  
FASTQ_REGEX = re.compile('^(\w{1,20})_R(\d{1,10})\.*')

## this will control the expected number of files
# found with prefix, for example, inputs/mysamples
EXPECTED_READS = int(os.environ['NUM_FASTQS_PER_SAMPLE'])
SFN_ARN = os.environ['GENOMICS_STEP_FUNCTION_ARN']

def get_files_with_prefix(_bucket, _key, _sample):
    file_list = []
    if "/" in _key:
        _prefix = os.path.dirname(_key) + '/' + _sample
    else:
        _prefix = _sample
    
    s3_client = boto3.client("s3")
    response = s3_client.list_objects_v2(Bucket=_bucket, Prefix=_prefix)
    files = response.get("Contents")
    for file in files:
        s3_file_uri = 's3://' + _bucket + '/' + file['Key']
        print(f"S3 file path: {s3_file_uri}")
        file_list.append(s3_file_uri)
    return file_list

def verify_fastq(_filename):
    result = re.search(FASTQ_REGEX, _filename)
    if result:
        print(f'verified that file {_filename} is a FASTQ')
        return True
    else:
        return False

def lambda_handler(event, context):
    # Sanity checks
    print("Received s3 event: " + json.dumps(event, indent=4))
    if "Records" not in event:
        sys.exit("Event doesnt have records, exiting")
    
    if len(event["Records"]) == 0:
        sys.exit("Event has empty records, exiting")

    event_obj = event["Records"][0]
    if "eventSource" not in event_obj or \
        event_obj["eventSource"] != "aws:s3" or \
            event_obj["eventName"].split(':')[0] != "ObjectCreated":
        sys.exit("Not a valid PutObject S3 event, exiting")
    
    # Get the object from the event and show its content type
    bucket = event_obj['s3']['bucket']['name']
    _key = event_obj['s3']['object']['key']
    print(f"Bucket: {bucket} Key: {_key}")

    if not _key.endswith('.fastq') and not _key.endswith('.fastq.gz'):
        sys.exit("Not a valid FASTQ file, exiting")
    else:
        # check if reads present
        if not verify_fastq(_key.split('/')[-1]):
            sys.exit("Not a valid fastq")
        else:
            result = re.match(FASTQ_REGEX, os.path.basename(_key))
            sample_name = result.group(1)
            files_for_sample = get_files_with_prefix(bucket, _key, sample_name)
            print(f"{len(files_for_sample)} reads found for sample {sample_name}")
            if len(files_for_sample) == EXPECTED_READS:
                print("All FASTQs for sample accounted for, start step functions")
                sfn_payload = {
                    "SampleId": sample_name,
                    "Read1":  files_for_sample[0],
                    "Read2": files_for_sample[1],
                    "SubjectId": 'TEST_SUBJECT',
                    "SequenceStoreId": os.environ["SEQUENCE_STORE_ID"],
                    "ReferenceArn": os.environ["REFERENCE_ARN"],
                    "WorkflowId": os.environ["WORKFLOW_ID"],
                    "WorkflowOutputS3Path": os.environ["WORKFLOW_OUTPUT_S3_PATH"],
                    "GatkDockerUri": os.environ["GATK_DOCKER_URI"],
                    "GotcDockerUri": os.environ["GOTC_DOCKER_URI"],
                    "IntervalsS3Path": os.environ["INTERVAL_S3_PATH"]
                }
                sfn_client = boto3.client('stepfunctions')
                try:
                    response = sfn_client.start_execution(
                        stateMachineArn=SFN_ARN,
                        name=f'GENOMICS_{sample_name}_' + str(uuid.uuid1()),
                        input=json.dumps(sfn_payload)
                    )
                except Exception as e:
                    raise e
            else:
                print("Not all FASTQs found for sample, exit")
