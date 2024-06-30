import json
import os
from .main import lambda_handler
import pytest
import boto3

@pytest.fixture
def transcription_bucket():
    os.environ["TRANSCRIPTIONS_BUCKET_NAME"] = "bucket"
    yield "bucket"

@pytest.fixture
def videos_table(dynamodb):
    os.environ["VIDEOS_TABLE_NAME"] = "videos-table"
    dynamodb.create_table(
        TableName="videos-table",
        KeySchema=[
            {"AttributeName": "PK", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "PK", "AttributeType": "S"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    table = boto3.resource("dynamodb").Table("videos-table")

    table.put_item(
        Item={
            "PK": "123",
            "language": "en-US"
        }
    )
    yield dynamodb
    

def test_transcribe_handler(transcription_bucket, videos_table, transcribe):

    event = {
        "Records": [
            {
                "Sns": {
                    "Message": json.dumps(
                        {
                            "video_id": "123",
                        }
                    )
                }
            }
        ]
    }

    lambda_handler(event, None)

    transcription_jobs = transcribe.list_transcription_jobs()["TranscriptionJobSummaries"]
    assert len(transcription_jobs) == 1
    assert transcription_jobs[0]["TranscriptionJobName"] == "123"
    assert transcription_jobs[0]["LanguageCode"] == "en-US"