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
    workflow_id = event['WorkflowId']
    role_arn = event['JobRoleArn']
    output_s3_path = event['OutputS3Path']
    params = {
        "sample_name": event['sample_name'],
        "ref_fasta": event['ref_fasta'],
        "fastq_1": event['fastq_1'],
        "fastq_2": event['fastq_2'],
        "readgroup_name": event['readgroup_name'],
        "library_name": event['fastq_2'],
        "platform_name": event['platform_name'],
        "run_date": event['run_date'],
        "sequencing_center":event['sequencing_center'],
        "dbSNP_vcf": event['dbSNP_vcf'],
        "Mills_1000G_indels_vcf": event['Mills_1000G_indels_vcf'],
        "known_indels_vcf": event['known_indels_vcf'],
        "scattered_calling_intervals_archive": event['scattered_calling_intervals_archive'],
        "gatk_docker": event['gatk_docker'],
        "gotc_docker": event['gotc_docker']
        
    }

    try:
        print("Attempt to start workflow run")
        response = omics_client.start_run(
            workflowId=workflow_id,
            name=event['sample_name'] + '-workflow',
            roleArn=role_arn,
            parameters=params,
            outputUri=output_s3_path
            )
    except ClientError as e:
        raise Exception( "boto3 client error : " + e.__str__())
    except Exception as e:
       raise Exception( "Unexpected error : " +    e.__str__())
    logger.info(response)
    return {"WorkflowRunId": response['id']}