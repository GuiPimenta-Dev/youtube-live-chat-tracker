import json
import os
from datetime import datetime, timedelta

import boto3
import sm_utils
from boto3.dynamodb.conditions import Key
from openai import OpenAI


def get_last_valid_end_time(transcription, key):
    for item in transcription:
        if "end_time" in item:
            try:
                end_time = float(item[key])
                return end_time
            except ValueError:
                continue
    return None


def convert_to_datetime(date_str: str) -> datetime:
    date_str = date_str.replace(" UTC", "")

    # Parse the string to a datetime object
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S%z")

    return dt


def convert_iso_to_custom_format(iso_str: str) -> str:
    """
    Convert an ISO 8601 string to the custom format 'YYYY-MM-DD HH:MM:SS UTC+0000'.

    :param iso_str: The ISO 8601 date string to convert.
    :return: The date string in the custom format.
    """
    # Parse the ISO 8601 date string
    dt = datetime.fromisoformat(iso_str)

    # Format the datetime object to the custom format
    custom_format = dt.strftime("%Y-%m-%d %H:%M:%S UTC%z")

    return custom_format


def lambda_handler(event, context):

    dynamodb = boto3.resource("dynamodb")

    body = json.loads(event["Records"][0]["body"])
    video_id = body["video_id"]
    transcription = body["transcription"]
    interval = body["interval"]
    start_time = body["start_time"]
    index = body["index"]
    print(f"Processing video {video_id} with interval {interval} and start time {start_time} and index {index}")

    TRANSCRIPTIONS_TABLE_NAME = os.environ.get("TRANSCRIPTIONS_TABLE_NAME", "Dev-Result")

    transcriptions_table = dynamodb.Table(TRANSCRIPTIONS_TABLE_NAME)

    transcription_start_date_in_seconds = get_last_valid_end_time(transcription, "start_time")
    transcription_end_date_in_seconds = get_last_valid_end_time(reversed(transcription), "end_time")

    transcription_start_timestamp = convert_to_datetime(start_time) + timedelta(
        seconds=transcription_start_date_in_seconds
    )
    transcription_end_timestamp = convert_to_datetime(start_time) + timedelta(seconds=transcription_end_date_in_seconds)

    transcription_start_timestamp = convert_iso_to_custom_format(transcription_start_timestamp.isoformat())
    transcription_end_timestamp = convert_iso_to_custom_format(transcription_end_timestamp.isoformat())

    content = ""
    for word in transcription:
        if word["type"] == "pronunciation":
            content += " " + word["alternatives"][0]["content"]

        else:
            content += word["alternatives"][0]["content"]

    CHATS_TABLE_NAME = os.environ.get("CHATS_TABLE_NAME", "Dev-Result")
    chats_table = dynamodb.Table(CHATS_TABLE_NAME)

    chat = chats_table.query(
        KeyConditionExpression=Key("PK").eq(video_id)
        & Key("SK").between(transcription_start_timestamp, transcription_end_timestamp)
    )["Items"]

    messages = [message["message"] for message in chat]

    OPENAPI_KEY_SECRET_NAME = os.environ["OPENAPI_KEY_SECRET_NAME"]
    api_key = sm_utils.get_secret(OPENAPI_KEY_SECRET_NAME)
    client = OpenAI(api_key=api_key)

    current_dir = os.path.dirname(os.path.realpath(__file__))
    prompt = open(f"{current_dir}/prompt.txt").read()

    author_summary = "Although my channel is focused on tech and programming, the primary focus of my channel is humor. So I would consider a good metric for my content to be how funny it is."

    items = {
        "author_summary": author_summary,
        "transcription": content.strip(),
        "chat": messages,
    }

    full_prompt = f"""{prompt}

{json.dumps(items)}
"""

    try:
        completion = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=1,
            max_tokens=4096,
            top_p=1,
            stream=False,
            response_format={"type": "json_object"},
            stop=None,
        )
        response = json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(e)
        response = {
            "rating": "N/A",
            "reason": "N/A",
            "transcription_summary": "N/A",
            "chat_summary": "N/A",
        }

    print(
        f"Adding transcription to the database for video {video_id} with interval {interval} in table {TRANSCRIPTIONS_TABLE_NAME}"
    )
    print(f"PK: {video_id}#INTERVAL={interval} Rating: {response['rating']} Reason: {response['reason']}")

    transcriptions_table.put_item(
        Item={
            "PK": f"{video_id}#INTERVAL={interval}",
            "SK": transcription_end_timestamp,
            "transcription": content.strip(),
            "chat": chat,
            "messages": messages,
            "rating": response["rating"],
            "reason": response["reason"],
            "transcription_summary": response["transcription_summary"],
            "chat_summary": response["chat_summary"],
        }
    )
