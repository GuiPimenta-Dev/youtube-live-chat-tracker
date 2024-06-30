import json
import os

import pytest
from .main import lambda_handler
from moto import mock_sqs
import boto3


@pytest.fixture
def sqs_client():
    with mock_sqs():
        sqs = boto3.client("sqs")
        sqs.create_queue(QueueName="test")
        response = sqs.get_queue_url(QueueName="test")
        queue_url = response["QueueUrl"]
        os.environ["DOWNLOADS_QUEUE_URL"] = queue_url
        yield boto3.client("sqs")


def test_it_should_publish_a_message_on_sqs_to_start_the_process(sqs_client):

    event = {"body": json.dumps({"url": "https://www.youtube.com/watch?v=5Zw0taVl2l0"})}
    lambda_handler(event, None)

    messages = sqs_client.receive_message(QueueUrl=os.environ["DOWNLOADS_QUEUE_URL"])["Messages"]

    message = json.loads(messages[0]["Body"])
    assert len(messages) == 1
    assert message["url"] == "https://www.youtube.com/watch?v=5Zw0taVl2l0"
    assert message["video_id"]
    assert message["language"] == "pt-BR"


def test_it_should_return_the_video_id(sqs_client):
    event = {"body": json.dumps({"url": "https://www.youtube.com/watch?v=5Zw0taVl2l0"})}
    response = lambda_handler(event, None)

    body = json.loads(response["body"])
    assert body["video_id"]
