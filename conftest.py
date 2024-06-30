import json
import os

import pytest
from moto import mock_sqs, mock_dynamodb, mock_s3, mock_sns
import boto3


@pytest.fixture
def sqs():
    with mock_sqs():
        yield boto3.client("sqs")


@pytest.fixture
def dynamodb():
    with mock_dynamodb():
        yield boto3.client("dynamodb")


@pytest.fixture
def s3():
    with mock_s3():
        yield boto3.client("s3", region_name="us-east-1")


@pytest.fixture
def sns():
    with mock_sns():
        yield boto3.client("sns")
