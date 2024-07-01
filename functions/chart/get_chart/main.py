from dataclasses import dataclass
import json
import os

import boto3

@dataclass
class Input:
    video_id: str
    interval: int = 10

@dataclass
class Output:
    message: str

def lambda_handler(event, context):

    video_id = event["queryStringParameters"]["video_id"]
    interval = event["queryStringParameters"].get("interval", 10)

    dynamodb = boto3.resource("dynamodb")
    TRANSCRIPTIONS_TABLE_NAME = os.environ.get("TRANSCRIPTIONS_TABLE_NAME", "Prod-Youtube-Live-Chat-Tracker-Live-Transcriptions")
    transcriptions_table = dynamodb.Table(TRANSCRIPTIONS_TABLE_NAME)

    data = transcriptions_table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("PK").eq(f"{video_id}#INTERVAL={interval}"),
        ProjectionExpression="SK, chat_summary, rating, reason",
    )["Items"]

    for item in data:
        item["hour"] = item.pop("SK")

    return {
        "statusCode": 200,
        "body": json.dumps({"data": data}, default=str),
        "headers": {"Access-Control-Allow-Origin": "*"},
    }
