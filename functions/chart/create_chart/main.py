import json
import os
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

import boto3


@dataclass
class Path:
    video_id: str


@dataclass
class Input:
    prompt: Optional[str] = ""
    interval: Optional[int] = 10
    min_messages: Optional[int] = 20


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
        discard = timedelta(minutes=dt.minute % int(interval), seconds=dt.second, microseconds=dt.microsecond)
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



import boto3
import json
import uuid

sqs = boto3.client('sqs')


def upload_to_s3(data, bucket_name):
    s3 = boto3.client('s3')
    key = f"large_payloads/{uuid.uuid4()}.json"
    s3.put_object(Bucket=bucket_name, Key=key, Body=json.dumps(data))
    return key


def send_message_to_sqs(video_id, batch, batches, interval, index, min_messages, prompt):
    TRANSCRIPT_QUEUE_URL = os.environ.get("TRANSCRIPT_QUEUE_URL")
    BUCKET_NAME = 'gui-docs'

    try:
        payload = {
            "video_id": video_id,
            "label": batch,
            "messages": batches[batch],
            "interval": interval,
            "index": index,
            "min_messages": min_messages,
            "prompt": prompt
        }
        
        payload_size = len(json.dumps(payload).encode('utf-8'))

        if payload_size > 256 * 1024:  # 256 KB
            s3_key = upload_to_s3(payload, BUCKET_NAME)
            message_body = json.dumps({
                "s3_bucket": BUCKET_NAME,
                "s3_key": s3_key
            })
        else:
            message_body = json.dumps(payload)

        sqs.send_message(
            QueueUrl=TRANSCRIPT_QUEUE_URL,
            MessageBody=message_body,
        )
    except Exception as e:
        print(e)


def lambda_handler(event, context):

    video_id = event["pathParameters"]["video_id"]

    body = json.loads(event["body"])
    interval = body.get("interval", 10)
    min_messages = body.get("min_messages", 20)
    prompt = body.get("prompt", "")

    print(f"Processing video {video_id} with interval {interval}")

    batches = group_chat_by_interval(partition_key=video_id, interval=interval)

    for index, batch in enumerate(batches):

        print(f"Sending batch {index + 1} to SQS")
        send_message_to_sqs(video_id, batch, batches, interval, index, min_messages, prompt)

    return {"statusCode": 200, "body": json.dumps({"message": "ok!"}), "headers": {"Access-Control-Allow-Origin": "*"}}
