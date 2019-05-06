# snapshotalyzer-30000
Demo project to maintain EC2 snapshots

## About

This project is a demo, and uses boto3 to manage AWS EC2 instance snapshots.

## Configuring

shotty uses the configurationn file created by AWS CLI e.g.

`aws configure --profile shotty`

##Running

`pipenv run python shotty.py <Command> <--project=PROJECT>`

*command* is list,start or stop
*project* is optional
