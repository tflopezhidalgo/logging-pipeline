import datetime

from shared import RouterPool, Router, InvalidParams


class WriterRouter(Router):

    def _validate_params(self, params):
        sanitized = {}

        if not params.get("app_id"):
            raise InvalidParams()

        sanitized["app_id"] = params.get("app_id")

        if not params.get("tags"):
            raise InvalidParams()

        sanitized["tags"] = params.get("tags")

        if not params.get("timestamp"):
            raise InvalidParams()

        sanitized["timestamp"] = datetime.datetime.fromisoformat(params.get("timestamp"))

        if not params.get("message"):
            raise InvalidParams()

        sanitized["message"] = params.get("message")

        return sanitized


class WriterRouterPool(RouterPool):
    def __init__(self, *args, **kwargs):
        super().__init__(router_class=WriterRouter, *args, **kwargs)
