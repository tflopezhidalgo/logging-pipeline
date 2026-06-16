import os
import datetime

from src.server.shared import RouterPool, Router, InvalidParams, InvalidAppID

LOGS_FOLDER = "/var/git/logging-pipeline/logs"


class ReaderRouter(Router):
    """
    Router for the reader endpoint. It validates the parameters and returns the logs
    """

    def _validate_params(self, params):
        sanitized = {}

        if not params.get("app_id"):
            raise InvalidParams()

        existent_app_ids = os.listdir(LOGS_FOLDER)

        app_id = params.get("app_id")
        if app_id not in existent_app_ids:
            raise InvalidAppID()

        sanitized["app_id"] = params.get("app_id")

        if params.get("from") and not params.get("to"):
            raise InvalidParams()

        if params.get("to") and not params.get("from"):
            raise InvalidParams()

        if params.get("to"):
            sanitized["to"] = datetime.datetime.fromisoformat(
                params.get("from")
            )

        if params.get("from"):
            sanitized["from"] = datetime.datetime.fromisoformat(
                params.get("to")
            )

        if params.get("tag"):
            sanitized["tag"] = params.get("tag")

        if params.get("pattern"):
            sanitized["pattern"] = params.get("pattern")

        return sanitized


class ReaderRouterPool(RouterPool):
    """
    ...

    """

    def __init__(self, *args, **kwargs):
        super().__init__(router_class=ReaderRouter, *args, **kwargs)
