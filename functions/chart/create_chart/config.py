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
            },
        )

        services.api_gateway.create_endpoint("POST", "/chart/{video_id}", function, public=True)

        services.sqs.grant_send_messages("transcript_queue", function)

