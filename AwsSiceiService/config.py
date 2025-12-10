import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_SESSION_TOKEN = os.environ.get("AWS_SESSION_TOKEN")
    S3_BUCKET = os.environ.get("S3_BUCKET")
    SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")
    DYNAMO_TABLE = os.environ.get("DYNAMO_TABLE", "sesiones-alumnos")

