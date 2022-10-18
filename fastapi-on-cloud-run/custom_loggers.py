import json
import yaml
import contextvars
import logging
import logging.config
from typing import Union
from datetime import date, datetime

logging.config.dictConfig(
    yaml.load(
        open("./logging_config.yaml").read(),
        Loader=yaml.SafeLoader
    )
)
env_name_context = contextvars.ContextVar[Union[str, None]](
    "env_name", default=None
)


class EnvNameFilter(logging.Filter):
    def filter(self, record):
        record.environment = env_name_context.get()
        return True


# Wrapper for logger to easy emit structured logs
class MainLogger:
    def __init__(self):
        self.logger = logging.getLogger("mainLogger")
        self.logger.addFilter(EnvNameFilter())

    def debug(self, msg: str, additional=None):
        self.logger.debug(msg=msg, extra=self.__build_extra(additional=additional))

    def info(self, msg: str, additional=None):
        self.logger.info(msg=msg, extra=self.__build_extra(additional=additional))

    def warning(self, msg: str, additional=None):
        self.logger.warning(msg=msg, extra=self.__build_extra(additional=additional))

    def error(self, msg: str, additional=None):
        self.logger.error(msg=msg, extra=self.__build_extra(additional=additional))

    def critical(self, msg: str, additional=None):
        self.logger.critical(msg=msg, extra=self.__build_extra(additional=additional))

    def __build_extra(self, additional) -> dict:
        """
        loggerのextra attributeとして渡すデータをCloud Logging側で
        JSONのvalidな要素として扱えるようにするための処理を行う
        具体的に書くとextra attributeに構造体を渡す場合、valueのデータはjson.dumpsされていないと
        Cloud Loggingでログ自体がjsonPayloadではなく、textPayloadとして扱われることがあるので
        jsonPayloadとして扱われるようにデータ構造を変更する
        """

        def __serializer_for_fallback(obj):
            """
            loggerの呼び出し側でシリアライズ可能かどうか意識させないために
            unserializable なデータの扱いに責任を持つメソッド
            """
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()

            if hasattr(obj, "__dict__"):
                return obj.__dict__

            raise TypeError("Type %s not serializable" % type(obj))

        try:
            extra = {"additional": json.dumps(additional, default=__serializer_for_fallback)}
        except TypeError as error:
            # 本番でない場合は気づきやすいように例外とし、本番の場合はシリアライズをスキップする
            # textPayloadにログが載ってしまうがアプリケーションが死ぬより良い
            if env_name_context.get() != "production":
                raise error

            self.logger.error(f"JSON Unserializable Object: {additional}")
            extra = {"additional": additional}

        return extra


main_logger = MainLogger()
"""Export Mainlogger instance as usual logger
Usage:
from custom_loggers import main_logger as logger

logger.info("logging message")
# You can pass extra data
logger.info(
    "another logging message",
    additional={"key1": 1, "key2": {"company": "sample"}, "key3": [1, 2, 3]}
)
logger.info("another logging message", additional="Yo!!")
"""
