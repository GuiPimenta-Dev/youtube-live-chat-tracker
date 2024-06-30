import json
import math
import os
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

import boto3


@dataclass
class Input:
    pass


@dataclass
class Output:
    message: str


def convert_to_minutes(duration):
    # Split the time string into hours, minutes, and seconds
    hours, minutes, seconds = map(int, duration.split(":"))

    # Create a timedelta object
    total_duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)

    # Convert the total duration to minutes
    total_minutes = total_duration.total_seconds() / 60
    return total_minutes


def convert_to_utc(date_str, date_format, original_offset_hours):
    # Parse the string date to a datetime object
    local_time = datetime.strptime(date_str, date_format)

    # Create a timezone object with the original offset
    original_timezone = timezone(timedelta(hours=original_offset_hours))

    # Set the timezone information to the datetime object
    local_time = local_time.replace(tzinfo=original_timezone)

    # Convert to UTC
    utc_time = local_time.astimezone(timezone.utc)

    return utc_time.isoformat()


def group_by_interval(data: Dict[str, Dict[str, Any]], interval: int) -> List[List[Dict[str, Any]]]:

    grouped_data = defaultdict(list)

    for entry in data:
        if "start_time" not in entry or "end_time" not in entry:
            continue

        start_time = float(entry["start_time"])
        end_time = float(entry["end_time"])

        # Determine the interval group for start and end times
        start_interval = int(start_time // interval)
        end_interval = int(end_time // interval)

        # Add the entry to the corresponding interval groups
        for i in range(start_interval, end_interval + 1):
            grouped_data[i].append(entry)

    # Convert the defaultdict to a sorted list of lists
    sorted_intervals = sorted(grouped_data.keys())
    grouped_list = [grouped_data[i] for i in sorted_intervals]

    return grouped_list


def lambda_handler(event, context):

    video_id = event["pathParameters"]["video_id"]
    interval = event["queryStringParameters"].get("interval", 10)
    start_time = event["queryStringParameters"].get("start_time", None)

    s3_client = boto3.client("s3")
    sqs = boto3.client("sqs", "us-east-2")
    TRANSCRIPT_QUEUE_URL = os.environ.get("TRANSCRIPT_QUEUE_URL")

    TRANSCRIPTIONS_BUCKET = os.environ.get("TRANSCRIPTIONS_BUCKET")

    key = f"{video_id}.json"

    response = s3_client.get_object(Bucket=TRANSCRIPTIONS_BUCKET, Key=key)
    body = json.loads(response["Body"].read())

    video_id = body["jobName"]
    transcription = body["results"]["items"]

    interval_in_seconds = int(interval) * 60
    batches = group_by_interval(transcription, interval_in_seconds)

    print(f"Transcription has been split into {len(batches)} batches")
    print(f"Sending batches to SQS ({TRANSCRIPT_QUEUE_URL})")

    for index, batch in enumerate(batches):
        print(f"Sending batch {index} to SQS")
        sqs.send_message(
            QueueUrl=TRANSCRIPT_QUEUE_URL,
            MessageBody=json.dumps(
                {
                    "video_id": video_id,
                    "transcription": batch,
                    "interval": interval,
                    "start_time": start_time,
                    "index": index,
                }
            ),
        )

    return {"statusCode": 200, "body": json.dumps({"message": "ok!"}), "headers": {"Access-Control-Allow-Origin": "*"}}
