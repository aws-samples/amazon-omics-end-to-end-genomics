import json
import boto3
from jsonschema import validate
from botocore.exceptions import ClientError

print('Loading function - Apply S3 Lifecycle')

s3_client = boto3.client('s3')

file_tag_rules = {
    "bam":
    [
        {
            "Key": "processed",
            "Value": "true"
        },
        {
            "Key": "OmicsTiering",
            "Value": "IntelligentTierAfter30"
        }
    ],
    "vcf":
    [
        {
            "Key": "processed",
            "Value": "true"
        },
        {
            "Key": "OmicsTiering",
            "Value": "Standard"
        }
    ],
    "gvcf":
    [
        {
            "Key": "processed",
            "Value": "true"
        },
        {
            "Key": "OmicsTiering",
            "Value": "IntelligentTierAfter30"
        }
    ],
    "fastq":
    [
        {
            "Key": "processed",
            "Value": "true"
        },
        {
            "Key": "OmicsTiering",
            "Value": "RemoveIn30"
        }
    ]
}

def validate_event(_event_json):
    schema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "properties": {
        "inputs": {
        "type": "object",
        "properties": {
            "fastq": {
                "type": "array"
            }
        },
        "required": [
            "fastq"
            ]
        },
        "outputs": {
            "type": "object",
            "properties": {
                "vcf": {
                    "type": "array"
                },
                "bam": {
                    "type": "array"
                },
                "gvcf": {
                    "type": "array"
                }
                },
            "required": [
                "vcf",
                "bam"
            ]
        }
    },
        "required": [
            "inputs",
            "outputs"
        ]
    }

    try:
        validate(_event_json, schema=schema)
        return True
    except Exception as e:
        raise e

def split_s3_path(s3_path):
    path_parts=s3_path.replace("s3://","").split("/")
    bucket=path_parts.pop(0)
    key="/".join(path_parts)
    return bucket, key

def get_tagset_for_object(_bucket, _key):
    try:
        get_tags_response = s3_client.get_object_tagging(
            Bucket=_bucket,
            Key=_key,
        )
        return get_tags_response['TagSet']
    except Exception as e:
        raise e

def lambda_handler(event, context):
    """
    Example event
    {
        "inputs": {
            "fastq": [
                "s3://path/tofastq_R1.fastq.gz",
                "s3://path/tofastq_R2.fastq.gz"
            ]
        },
        "outputs": {
            "vcf": [
                "s3://output.vcf"
            ],
            "bam": [
                "s3://output.bam"
            ],
            "gvcf": [
                "s3://example.genome.vcf.gz"
            ]
        } 
    }
    """
    # Inoked by Step Function 
    print("Received event: " + json.dumps(event, indent=2))

    objects_to_tag = {}
    # check valid event and add files to tag
    if validate_event(event):
        for _k, _v in event['inputs'].items():
            objects_to_tag[_k] = _v
        for _k, _v in event['outputs'].items():
            objects_to_tag[_k] = _v

    # check and apply tags based on config
    for file_type, s3_files in objects_to_tag.items():
        for _s3_file in s3_files:
            bucket, _key = split_s3_path(_s3_file)
            print(f"File type: {file_type} Bucket: {bucket} Key: {_key}")
            # tag_set = get_tagset_for_object(bucket, _key)
            # Add logic here to check existing tags if needed

            # Apply new tag set based on file type and config
            try:
                put_tags_response = s3_client.put_object_tagging(
                    Bucket=bucket,
                    Key=_key,    
                    Tagging={
                        'TagSet': file_tag_rules[file_type]
                    }
                )
                print(put_tags_response)
            except ClientError as e:
                raise Exception( "boto3 client error : " + e.__str__())
            except Exception as e:
                raise Exception( "Unexpected error : " +    e.__str__())
    print("Cleanup complete for sample")
