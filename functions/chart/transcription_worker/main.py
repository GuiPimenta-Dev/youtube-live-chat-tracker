import json
import os

import boto3
import sm_utils
from openai import OpenAI


def lambda_handler(event, context):

    dynamodb = boto3.resource("dynamodb")

    body = json.loads(event["Records"][0]["body"])
    video_id = body["video_id"]
    chat = body["messages"]
    label = body["label"]
    interval = body["interval"]
    index = body["index"]
    print(f"Processing video {video_id} with interval {interval} and index {index}")

    TRANSCRIPTIONS_TABLE_NAME = os.environ.get("TRANSCRIPTIONS_TABLE_NAME", "Dev-Result")

    transcriptions_table = dynamodb.Table(TRANSCRIPTIONS_TABLE_NAME)

    messages = [message["message"] for message in chat]

    OPENAPI_KEY_SECRET_NAME = os.environ.get("OPENAPI_KEY_SECRET_NAME", "OPEN_API_KEY")
    api_key = sm_utils.get_secret(OPENAPI_KEY_SECRET_NAME)
    client = OpenAI(api_key=api_key)

    current_dir = os.path.dirname(os.path.realpath(__file__))
    prompt = open(f"{current_dir}/prompt.txt").read()

    author_summary = "Although my channel is focused on tech and programming, the primary focus of my channel is humor. So I would consider a good metric for my content to be how funny it is."

    items = {
        "author_summary": author_summary,
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
            "chat_summary": "N/A",
        }

    print(
        f"Adding transcription to the database for video {video_id} with interval {interval} in table {TRANSCRIPTIONS_TABLE_NAME}"
    )
    print(f"PK: {video_id}#INTERVAL={interval} Rating: {response['rating']} Reason: {response['reason']}")

    transcriptions_table.put_item(
        Item={
            "PK": f"{video_id}#INTERVAL={interval}",
            "SK": label,
            "chat": chat,
            "messages": messages,
            "rating": response["rating"],
            "reason": response["reason"],
            "chat_summary": response["chat_summary"],
        }
    )
