from aws_cdk import aws_iam as iam

from infra.services import Services


class CreateChartConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="CreateChart",
            path="./functions/chart",
            description="Parse the transcription",
            directory="create_chart",
            environment={
                "TRANSCRIPT_QUEUE_URL": services.sqs.transcript_queue.queue_url,
                "CHAT_TABLE_NAME": services.dynamodb.chats_table.table_name,
            },
        )

        services.api_gateway.create_endpoint("POST", "/chart/{video_id}", function, public=True)

        services.sqs.grant_send_messages("transcript_queue", function)

        services.s3.large_payload_bucket.grant_read_write(function)
        
        function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["dynamodb:Query"],
                resources=["*"],
            )
        )
