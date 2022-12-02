#!/bin/bash

set -e 

ARTIFACT_S3_BUCKET=s3://${1}
AWS_PROFILE=$2
TEMPLATES='templates'
LAMBDAS='lambdas'
WORKFLOWS='workflows'
BUILDSPECS='buildspecs'

# use profile if 2nd argument provided
if [ $# -eq 2 ]
  then
    AWS_PROFILE=" --profile ${2}"
fi

echo "=========================================="
echo "TRIGGER CODEBUILD JOB LAMBDAS"
echo "=========================================="
cd ../src/lambda/trigger_code_build
echo "Installing pip packages"
pip3 install crhelper -t ./package
cd ./package
zip -r ../trigger_docker_code_build.zip .
cd ..
echo "Zip lambda to artifact"
zip -g trigger_docker_code_build.zip trigger_docker_code_build.py
aws s3 cp trigger_docker_code_build.zip $ARTIFACT_S3_BUCKET/$LAMBDAS/ $AWS_PROFILE
rm trigger_docker_code_build.zip 
echo "done with trigger_docker_code_build.zip"

cd ./package
zip -r ../trigger_lambdas_code_build.zip .
cd ..
echo "Zip lambda to artifact"
zip -g trigger_lambdas_code_build.zip trigger_lambdas_code_build.py
aws s3 cp trigger_lambdas_code_build.zip $ARTIFACT_S3_BUCKET/$LAMBDAS/ $AWS_PROFILE
rm trigger_lambdas_code_build.zip
rm -r ./package
echo "done with trigger_lambdas_code_build.zip"
echo "Uploaded all lambdas Zip files to trigger Code Build jobs to ${ARTIFACT_S3_PATH}/${LAMBDAS}/"

echo "=========================================="
echo "UPLOAD CLOUDFORMATION TEMPLATES"
echo "=========================================="
echo "iterate through cfn templates and upload to s3"
cd ../../../deploy
for f in $(find ../src/cfn_templates/ -name '*.yml' -or -name '*.yaml'); do echo "uploading `basename $f`" && aws s3 cp $f $ARTIFACT_S3_BUCKET/$TEMPLATES/ $AWS_PROFILE && echo "Done"; done
echo "Uploaded all cfn template files to ${ARTIFACT_S3_PATH}/${TEMPLATES}/"

echo "=========================================="
echo "ZIP and UPLOAD WORKFLOW FILES"
echo "=========================================="
echo "zip and upload workflow files "
cd ../src/workflow/
zip -r gatkbestpractices.wdl.zip main.wdl sub-workflows/
aws s3 cp gatkbestpractices.wdl.zip $ARTIFACT_S3_BUCKET/$WORKFLOWS/ $AWS_PROFILE
aws s3 cp parameter-template.json $ARTIFACT_S3_BUCKET/$WORKFLOWS/ $AWS_PROFILE
rm gatkbestpractices.wdl.zip
echo "uploaded all workflow files to ${ARTIFACT_S3_BUCKET}/${WORKFLOWS}/"
cd -

echo "=========================================="
echo "UPLOAD LAMBDA FILES"
echo "=========================================="
echo "iterate through lambdas and upload to s3"
for f in $(find ../src/lambda/ -name '*.py' -or -name '*.py'); do echo "uploading `basename $f`" && aws s3 cp $f $ARTIFACT_S3_BUCKET/$LAMBDAS/ $AWS_PROFILE && echo "Done"; done
echo "Uploaded all lambda files to ${ARTIFACT_S3_BUCKET}/${LAMBDAS}/"

echo "=========================================="
echo "UPLOAD CODEBUILD BUILDSPEC FILES"
echo "=========================================="
echo "iterate through buildspecs and upload to s3"
for f in $(find ../src/codebuild/ -name '*.yml' -or -name '*.yaml'); do echo "uploading `basename $f`" && aws s3 cp $f $ARTIFACT_S3_BUCKET/$BUILDSPECS/ $AWS_PROFILE && echo "Done"; done
echo "Uploaded all buildspec files to ${ARTIFACT_S3_BUCKET}/${BUILDSPECS}/"

echo "=========================================="
echo "DONE"
echo "=========================================="