import json
import os

import pytest

from conftest import simplify_dynamodb_item

from .main import lambda_handler


@pytest.fixture
def videos_bucket(s3):
    s3.create_bucket(Bucket="videos_bucket")
    os.environ["VIDEOS_BUCKET_NAME"] = "videos_bucket"
    yield s3


@pytest.fixture
def videos_table(dynamodb):
    dynamodb.create_table(
        TableName="videos_table",
        KeySchema=[{"AttributeName": "PK", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "PK", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    os.environ["VIDEOS_TABLE_NAME"] = "videos_table"
    yield dynamodb


@pytest.fixture
def videos_topic(sns):
    topic = sns.create_topic(Name="videos_topic")
    os.environ["VIDEOS_TOPIC_ARN"] = topic["TopicArn"]
    yield sns


def test_it_should_download_a_video_and_trigger_the_correct_events(videos_bucket, videos_table, videos_topic):

    event = {
        "Records": [
            {
                "body": json.dumps(
                    {
                        "url": "https://www.youtube.com/watch?v=5Zw0taVl2l0",
                        "video_id": "5Zw0taVl2l0",
                        "language": "pt-BR",
                    }
                )
            }
        ]
    }

    lambda_handler(event, None)

    video_on_bucket = videos_bucket.list_objects_v2(Bucket="videos_bucket")["Contents"][0]
    video_on_table = simplify_dynamodb_item(
        videos_table.get_item(TableName="videos_table", Key={"PK": {"S": "5Zw0taVl2l0"}})["Item"]
    )

    assert video_on_bucket["Key"] == "5Zw0taVl2l0.mp3"
    assert video_on_table == {
        "PK": "5Zw0taVl2l0",
        "duration": "02:57:49",
        "language": "pt-BR",
        "publish_date": "2024-06-19T00:00:00",
        "title": "reagindo projetos, portfólio, github, linkedin // SEJA MEMBRO",
        "url": "https://www.youtube.com/watch?v=5Zw0taVl2l0",
    }
