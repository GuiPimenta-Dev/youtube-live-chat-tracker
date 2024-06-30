import json
import os

import boto3


def lambda_handler(event, context):

    video_id = event["queryStringParameters"]["video_id"]
    interval = event["queryStringParameters"].get("interval", 10)

    dynamodb = boto3.resource("dynamodb")
    TRANSCRIPTIONS_TABLE_NAME = os.environ.get("TRANSCRIPTIONS_TABLE_NAME", "Dev-Transcriptions")
    transcriptions_table = dynamodb.Table(TRANSCRIPTIONS_TABLE_NAME)

    data = transcriptions_table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("PK").eq(f"{video_id}#INTERVAL={interval}")
    )["Items"]

    return {
        "statusCode": 200,
        "body": json.dumps({"data": data}, default=str),
        "headers": {"Access-Control-Allow-Origin": "*"},
    }
