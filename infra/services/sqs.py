from aws_cdk import Duration, aws_lambda_event_sources
from aws_cdk import aws_sqs as sqs

from lambda_forge.trackers import invoke, trigger


class SQS:
    def __init__(self, scope, context) -> None:

        self.downloads_queue = sqs.Queue(
            scope,
            "DownloadsQueue",
            queue_name=f"{context.stage.lower()}-downloads",
            visibility_timeout=Duration.minutes(15),
        )

        self.transcript_queue = sqs.Queue(
            scope,
            "TranscriptQueue",
            queue_name=f"{context.stage.lower()}-transcript",
        )

    @trigger(service="sqs", trigger="queue", function="function")
    def create_trigger(self, queue, function):
        queue = getattr(self, queue)
        event_source = aws_lambda_event_sources.SqsEventSource(queue)
        function.add_event_source(event_source)
        queue.grant_consume_messages(function)

    @invoke(service="sqs", resource="queue", function="function")
    def grant_send_messages(self, queue, function):
        queue = getattr(self, queue)
        queue.grant_send_messages(function)
