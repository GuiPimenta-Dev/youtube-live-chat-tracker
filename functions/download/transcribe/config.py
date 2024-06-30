from infra.services import Services
from aws_cdk import aws_iam as iam

class TranscribeConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Transcribe",
            path="./functions/download",
            directory="transcribe",
            description="Transcript audio to text",
            environment={
                "TRANSCRIPTIONS_BUCKET_NAME": services.s3.transcriptions_bucket.bucket_name,
                "VIDEOS_TABLE_NAME": services.dynamodb.videos_table.table_name,
            },
        )

        services.sns.create_trigger("videos_topic", function)
        
        services.s3.grant_write("transcriptions_bucket",function)
        services.s3.videos_bucket.grant_read(function)
        
        services.dynamodb.videos_table.grant_read_data(function)
        
        function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["transcribe:StartTranscriptionJob"],
                resources=["*"],
            )
        )