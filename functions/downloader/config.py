from infra.services import Services


class DownloaderConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Downloader",
            path="./functions/downloader",
            description="Download a YouTube video and Stores it on S3",
        )

        services.sqs.create_trigger("downloads_queue", function)

        services.s3.grant_write("videos_bucket", function)

        services.dynamodb.grant_write("videos_table", function)

        services.sns.grant_publish("videos_topic", function)
