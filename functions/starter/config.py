from infra.services import Services


class StarterConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Starter",
            path="./functions/starter",
            description="Start the process",
        )

        services.api_gateway.create_endpoint("POST", "/starter", function)
