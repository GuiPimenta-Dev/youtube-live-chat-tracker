from aws_cdk import aws_lambda as _lambda
from lambda_forge.path import Path


class Layers:
    def __init__(self, scope) -> None:

        self.pytube_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id="PytubeLayer",
            layer_version_arn="arn:aws:lambda:us-east-2:211125768252:layer:pytube:1",
        )

        self.chat_downloader_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id="ChatDownloaderLayer",
            layer_version_arn="arn:aws:lambda:us-east-2:211125768252:layer:chat_downloader:1",
        )

        self.pandas_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id="PandasLayer",
            layer_version_arn="arn:aws:lambda:us-east-2:770693421928:layer:Klayers-p39-pandas:22",
        )

        self.numpy_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id="NumpyLayer",
            layer_version_arn="arn:aws:lambda:us-east-2:770693421928:layer:Klayers-p39-numpy:17",
        )
