import datetime
import json
import os

import boto3
from chat_downloader import ChatDownloader as cd


def lambda_handler(event, context):

    dynamodb = boto3.resource("dynamodb", region_name="us-east-2")

    CHAT_TABLE_NAME = os.environ.get("CHAT_TABLE_NAME", "Dev-Chats")
    chats_table = dynamodb.Table(CHAT_TABLE_NAME)

    record = event["Records"][0]
    message = json.loads(record["Sns"]["Message"])

    video_id = message["video_id"]
    url = message["url"]

    chat = cd().get_chat(url)

    for message in chat:
        timestamp_seconds = message["timestamp"] / 1_000_000
        utc_datetime = datetime.datetime.utcfromtimestamp(timestamp_seconds)

        # Attach the UTC timezone
        utc_datetime = utc_datetime.replace(tzinfo=datetime.timezone.utc)

        # Format the datetime string to include the timezone information
        formatted_date = utc_datetime.strftime("%Y-%m-%d %H:%M:%S %Z%z")

        chats_table.put_item(
            Item={
                "PK": video_id,
                "SK": formatted_date,
                "message": message["message"],
                "author": message["author"],
            }
        )
