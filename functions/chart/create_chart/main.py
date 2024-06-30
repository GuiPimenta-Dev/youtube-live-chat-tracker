import json
import os
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

import boto3
from boto3.dynamodb.conditions import Key


@dataclass
class Input:
    pass


@dataclass
class Output:
    message: str


def group_chat_by_interval(partition_key, interval):

    session = boto3.Session()

    dynamodb = session.resource("dynamodb")
    CHAT_TABLE_NAME = os.environ.get("CHAT_TABLE_NAME", "Dev-Chats")
    table = dynamodb.Table(CHAT_TABLE_NAME)

    response = table.query(KeyConditionExpression=boto3.dynamodb.conditions.Key("PK").eq(partition_key))

    items = response["Items"]

    # Function to round down to the nearest 10-minute interval
    def round_time(dt, interval=interval):
        discard = timedelta(minutes=dt.minute % interval, seconds=dt.second, microseconds=dt.microsecond)
        return dt - discard

    def format_time_label(dt):
        total_minutes = dt.hour * 60 + dt.minute
        minutes = total_minutes % 60
        hours = total_minutes // 60
        return f"{hours:02d}:{minutes:02d}"

    # Group items by 10-minute intervals
    grouped_items = defaultdict(list)
    for item in items:
        sk = item["SK"]
        sk = sk.replace(" UTC+0000", "")
        sk_datetime = datetime.strptime(sk, "%Y-%m-%d %H:%M:%S")
        rounded_time = round_time(sk_datetime)
        time_label = format_time_label(rounded_time)
        grouped_items[time_label].append(item)

    return grouped_items


def lambda_handler(event, context):

    video_id = event["pathParameters"]["video_id"]
    interval = event["queryStringParameters"].get("interval", 10)

    print(f"Processing video {video_id} with interval {interval}")

    sqs = boto3.client("sqs", "us-east-2")

    TRANSCRIPT_QUEUE_URL = os.environ.get("TRANSCRIPT_QUEUE_URL")

    batches = group_chat_by_interval(partition_key=video_id, interval=interval)

    for index, batch in enumerate(batches):

        print(f"Sending batch {index + 1} to SQS")
        sqs.send_message(
            QueueUrl=TRANSCRIPT_QUEUE_URL,
            MessageBody=json.dumps(
                {
                    "video_id": video_id,
                    "label": batch,
                    "messages": batches[batch],
                    "interval": interval,
                    "index": index,
                },
                default=str,
            ),
        )

    return {"statusCode": 200, "body": json.dumps({"message": "ok!"}), "headers": {"Access-Control-Allow-Origin": "*"}}
