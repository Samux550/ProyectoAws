import boto3
import os

def boto3_client(service, region_name=None):
    region = region_name or os.environ.get("AWS_REGION")
    kwargs = {}
    if region:
        kwargs["region_name"] = region

    ak = os.environ.get("AWS_ACCESS_KEY_ID")
    sk = os.environ.get("AWS_SECRET_ACCESS_KEY")
    token = os.environ.get("AWS_SESSION_TOKEN")

    if ak and sk:
        kwargs.update({
            "aws_access_key_id": ak,
            "aws_secret_access_key": sk
        })
    if token:
        kwargs["aws_session_token"] = token

    return boto3.client(service, **kwargs)

def boto3_resource(service, region_name=None):
    region = region_name or os.environ.get("AWS_REGION")
    kwargs = {}
    if region:
        kwargs["region_name"] = region

    ak = os.environ.get("AWS_ACCESS_KEY_ID")
    sk = os.environ.get("AWS_SECRET_ACCESS_KEY")
    token = os.environ.get("AWS_SESSION_TOKEN")

    if ak and sk:
        return boto3.resource(service, region_name=region,
                              aws_access_key_id=ak,
                              aws_secret_access_key=sk,
                              aws_session_token=token)
    else:
        return boto3.resource(service, region_name=region)
