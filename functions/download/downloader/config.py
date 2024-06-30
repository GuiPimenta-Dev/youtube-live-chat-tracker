from infra.services import Services


class DownloaderConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Downloader",
            path="./functions/download",
            directory="downloader",
            description="Download a YouTube video and Stores it on S3",
            layers=[services.layers.pytube_layer],
            memory_size=512,
            timeout=15,
            environment={
                "VIDEOS_BUCKET_NAME": services.s3.videos_bucket.bucket_name,
                "VIDEOS_TABLE_NAME": services.dynamo_db.videos_table.table_name,
                "VIDEOS_TOPIC_ARN": services.sns.videos_topic.topic_arn,
            },
        )

        services.sqs.create_trigger("downloads_queue", function)

        services.s3.grant_write("videos_bucket", function)

        services.dynamodb.grant_write("videos_table", function)

        services.sns.grant_publish("videos_topic", function)
