import json
import os

import pytest
from moto import mock_sqs
import boto3


@pytest.fixture
def sqs():
    with mock_sqs():
        yield boto3.client("sqs")

@pytest.fixture
def downloads_queue(sqs):
    sqs.create_queue(QueueName="downloads_queue")
    response = sqs.get_queue_url(QueueName="downloads_queue")
    queue_url = response["QueueUrl"]
    os.environ["DOWNLOADS_QUEUE_URL"] = queue_url
    yield sqs