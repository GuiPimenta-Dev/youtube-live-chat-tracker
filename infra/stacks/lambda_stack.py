from functions.chart.get_chart.config import GetChartConfig
from aws_cdk import Stack
from constructs import Construct

from functions.chart.create_chart.config import CreateChartConfig
from functions.chart.transcription_worker.config import \
    TranscriptionWorkerConfig
from functions.download.downloader.config import DownloaderConfig
from functions.download.get_chat.config import GetChatConfig
from functions.download.starter.config import StarterConfig
from functions.download.transcribe.config import TranscribeConfig
from infra.services import Services


class LambdaStack(Stack):
    def __init__(self, scope: Construct, context, **kwargs) -> None:

        super().__init__(scope, f"{context.name}-Lambda-Stack", **kwargs)

        self.services = Services(self, context)

        # Starter
        StarterConfig(self.services)

        # Downloader
        DownloaderConfig(self.services)

        # GetChat
        GetChatConfig(self.services)

        # Download
        TranscribeConfig(self.services)

        # Chart
        GetChartConfig(self.services)
        TranscriptionWorkerConfig(self.services)
        CreateChartConfig(self.services)
