# Amazon Omics - from raw sequence data to insights

This github repository has the code and artifacts described in the blog post: [Part 2 – Automated End to End Genomics Data Processing and Analysis using Amazon Omics and AWS Step Functions](https://aws.amazon.com/blogs/industries/automated-end-to-end-genomics-data-storage-and-analysis-using-amazon-omics/):


## Reference architecture
![Alt text](static/arch_diagram.png?raw=true "Reference architecture using Step Functions and Lambda Functions")

## Prerequisites 

- Python 3.7 and above with package installer - pip
- Linux/UNIX environment to run deployment shell scripts
- Compression and file packaging utility - zip
- AWS account with AdminstratorAccess to deploy various AWS resources using CloudFormation
- An S3 bucket, for example `my-artifact-bucket` within this account to upload all assets needed for deployment
- AWS CLI v2 installed and configured to your AWS Account to upload files to `<my-artifact-bucket>` (Installation instructions here: https://github.com/aws/aws-cli/tree/v2#installation)


```
Note that cross region imports are not supported in Amazon Omics today. If you chose to deploy it in another supported region outside of us-east-1, copy the example data used in the solution in a bucket in that region and update the permissions in the CloudFormation templates accordingly
```

## How to deploy

1. Once you clone the repository, navigate to the `deploy/` directory within the repository.  
2. Run the deployment script to upload all required files to the artifact bucket

`sh upload_artifacts my-artifact-bucket <aws-profile-name>`
```
NOTE

You can use the 2nd argument <aws-profile-name> as an optional argument if you chose to use a specific AWS profile
```
3. Navigate to the AWS S3 Console. In the list of buckets, click on `<my-artifact-bucket>` and navigate to `templates` prefix. Find the file named `solution-cfn.yml`. Copy the Object URL (begins with https://) for this object (not the S3 URI).
4. Navigate to AWS CloudFormation Console. Click on `Create Stack`, select `Template is ready` and paste the above https:// Object URL into the `Amazon S3 URL` field and click `Next`. 
5. Fill in the `Stack name` with a name of your choice, `ArtifactBucketName` with `<my-artifact-bucket>`, `WorkflowInputsBucketName` & `WorkflowOutputsBucketName` with new bucket names of your choice; these buckets will be created.
6. For the `CurrentReferenceStoreId` parameter, if the account that you plan to use has an existing reference store and you want to repurpose it, you can provide the Referernce store ID as the value. (Since only 1 reference store is allowed per account per region). If you don't have one and want to create a new one, provide the value `NONE`. 
7. Click Next on the subsequent two pages, then on the Review <Stack name> page, acknowledge the following 'Capabilities', and click `Submit`:
    - AWS CloudFormation might create IAM resources with custom names.
    - AWS CloudFormation might require the following capability: CAPABILITY_AUTO_EXPAND
8. CloudFormation will now create multiple stacks with all the necessary resources, including Omics resources:
    - Omics Reference Store with Reference genome imported (Skip Reference store creation if store ID provided)
    - Omics Sequence Store
    - Omics Workflow with workflow definition and parameters defined
    - Omics Variant Store
    - Omics Annotation Store with ClinVar imported

9. It's recommended that users update omics permissions to least privilege access when leveraging this sample code as a starting point for future production needs.
10. The CloudFormation Stack should complete deployment in less than an hour

## Usage
1. Once the template has been deployed successfully, you can use a pair of FASTQ files to launch the end to end Secondary Analysis pipeline. 

```
Note that in this solution, the FASTQ files need to be named in the following manner:
    
<sample_name>_R1.fastq.gz 

<sample_name>_R2.fastq.gz

This can be updated to your needs by updating the Python regex in start_workflow_lambda.py

You can also use example FASTQs provided here to test:

s3://aws-genomics-static-us-east-1/omics-e2e/test_fastqs/NA1287820K_R1.fastq.gz
    
s3://aws-genomics-static-us-east-1/omics-e2e/test_fastqs/NA1287820K_R2.fastq.gz

```


2. Upload these FASTQ files to the bucket used for `WorkflowInputsBucketName` in a prefix `inputs`. This bucket is configured such that uploaded FASTQ files in this prefix will use S3 notifications to tigger a Lambda function that evaluates the inputs and launches the Step Functions workflow. You can monitor the Step Functions workflow in the AWS Console for Step Functions and navigating to State Machines -> AmazonOmicsEndToEndStepFunction. You should see a running Execution with the Name "GENOMICS_\<sampleId>_\<uuid>", where sampleId is extracted from the name of the FASTQ files used.

```
NOTE

Currently if both FASTQs are uploaded simultaneaously, the Step Function trigger lambda has a best-effort mechanism to avoid race conditions by adding a random delay and checking for a running execution with the same sample name. It's recommended to check for a duplicate execution as a precaution.
```

3. The Step Functions workflow has the following steps:
   - Import FASTQ files to the pre-created Omics Sequence store.
   - Start a pre-created Omics Workflow with the input FASTQs.
   - Import the workflow output BAM file to the pre-created Omics Sequence Store and the output VCF file to the pre-created Omics Variant Store in parallel.
   - Apply S3 object tags to the input FASTQ and output BAM and VCF files to allow S3 lifecycle policies to be applied.  
   
![Alt text](static/stepfunctions_graph_workflowstudio.png?raw=true "Step Function State Machine")

4. Since these steps are asynchronous API calls, we leverage tasks to poll for completion and move on to the next step on success. The Step Functions Workflow takes about 3 hours to complete with the test FASTQs provided above and could vary by the size of inputs chosen. 

    Note that if there is a Step Function Workflow failure, users can refer to this blog on instructions for how to resume a Step Function workflow - https://aws.amazon.com/blogs/compute/resume-aws-step-functions-from-any-state/

5. Now that the variants are available in the Omics Variant Store and the pre-loaded annotations in the Omics Annotation store, you can create resource links for them in AWS Lake Formation, Grant permissions to the desired users and query the resuting tables in Amazon Athena to derive insights (see instructions on how to provide Lake Formation permissions in the blog post <link>). Note that for the example notebook, we used genomic data from the example [Ovation Dx NAFLD Whole Genome dataset](https://aws.amazon.com/marketplace/pp/prodview-565xa6uzf77wu?sr=0-1&ref_=beagle&applicationId=AWS-Marketplace-Console#offers) from the Amazon Data Exchange

## Cleanup

The above solution has deployed several AWS resources as part of the CloudFormation stack. If you chose to clean up the resources created by this solution, you can take the following steps:

1. Delete the CloudFormation stack with the name that was assigned at creation. This will start deleting all the resources created. 
2. Due to certain actions taken during usage of the solution, resources such as the Workflow input and output buckets and the ECR respoistories will fail to delete due to them not being empty. In order to delete them as well, users will have to empty the contents of the S3 buckets for Workflow inputs and outputs and delete the images created under the Amazon ECR repositories (if you chose to clean up these resources). Once deleted, you can re-attempt to delete the CloudFormation stack.
3. If the Omics resources fail to delete by the delete stack action in CloudFormation, users will need to manually delete the Omics Resources created by the stack, such as the workfow, variant store, annotation store, sequence store and reference store (or just the imported reference genome). Once done, you can re-attempt to delete the CloudFormation stack.  
4. If certain custom CloudFormation resources such as Lambda functions in the Omics and CodeBuild stacks fail to delete again, simply retrying the deletion of the parent stack should delete it.
   

## License
This library is licensed under the MIT-0 License. See the LICENSE file.

## Authors

Nadeem Bulsara | Sr. Solutions Architect - Genomics, BDSI | AWS

Sujaya Srinivasan | Genomics Solutions Architect, WWPS | AWS 

David Obenshain | Cloud Application Architect, WWPS Professional Services | AWS

Gargi Singh Chhatwal | Sr. Solutions Architect - Federal Civilian, WWPS | AWS

Joshua Broyde | Sr. AI/ML Solutions Architect, BDSI | AWS