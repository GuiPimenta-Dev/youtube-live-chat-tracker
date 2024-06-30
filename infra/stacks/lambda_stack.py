from aws_cdk import Stack
from constructs import Construct

from functions.downloader.config import DownloaderConfig
from functions.starter.config import StarterConfig
from infra.services import Services


class LambdaStack(Stack):
    def __init__(self, scope: Construct, context, **kwargs) -> None:

        super().__init__(scope, f"{context.name}-Lambda-Stack", **kwargs)

        self.services = Services(self, context)

        # Starter
        StarterConfig(self.services)

        # Downloader
        DownloaderConfig(self.services)
