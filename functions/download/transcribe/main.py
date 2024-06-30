import json
import os

import boto3


def lambda_handler(event, context):

    TRANSCRIPTIONS_BUCKET_NAME = os.environ.get("TRANSCRIPTIONS_BUCKET_NAME", "live-cut-the-bullshit-transcriptions")
    VIDEOS_TABLE_NAME = os.environ.get("VIDEOS_TABLE_NAME", "Dev-Videos")

    transcribe_client = boto3.client("transcribe")
    dynamodb = boto3.resource("dynamodb")

    record = event["Records"][0]
    message = json.loads(record["Sns"]["Message"])

    video_id = message["video_id"]

    bucket_name = "dev-videos-bucket"
    object_key = f"{video_id}.mp3"
    
    job_uri = f"s3://{bucket_name}/{object_key}"

    print(f"Starting transcription job for {job_uri}")
    
    videos_table = dynamodb.Table(VIDEOS_TABLE_NAME)
    video = videos_table.get_item(Key={"PK": video_id})["Item"]

    print(f"Transcribing video {video_id} in {video['language']}")
    
    print(f"Transcription will be stored in {TRANSCRIPTIONS_BUCKET_NAME}")

    transcribe_client.start_transcription_job(
        TranscriptionJobName=video_id,
        Media={"MediaFileUri": job_uri},
        MediaFormat="mp3",
        LanguageCode=video["language"],
        OutputBucketName=TRANSCRIPTIONS_BUCKET_NAME,
    )

