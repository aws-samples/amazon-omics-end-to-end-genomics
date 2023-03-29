# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] (2023-03-29)

### Features

* Removed dependency on Omics API models as a Lambda Layer due to general availablility
* Use Omics CloudFormation resources instead of Custom Resources
* Introduce checks in Step Functions State Machine to prevent duplicate workflows from being launched
* Use existing Omics Reference store, if provided, else create a new one 

## [1.0.0] (2022-11-30)

### Features

* First releasw