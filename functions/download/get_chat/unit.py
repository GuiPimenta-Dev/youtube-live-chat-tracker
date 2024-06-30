import json
import os

import pytest

from .main import lambda_handler


@pytest.fixture
def chats_table(dynamodb):
    os.environ["CHAT_TABLE_NAME"] = "table"
    yield dynamodb


def test_lambda_handler(chats_table):

    event = {
        "Records": [
            {
                "Sns": {
                    "Message": json.dumps(
                        {
                            "video_id": "123",
                            "url": "https://www.youtube.com/watch?v=5Zw0taVl2l0",
                        }
                    )
                }
            }
        ]
    }

    lambda_handler(event, None)

    assert chats_table.scan(TableName="table")["ScannedCount"] == 3668
