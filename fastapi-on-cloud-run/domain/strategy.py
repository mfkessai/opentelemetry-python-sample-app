from trace import add_trace_span
from custom_loggers import main_logger


class Strategy:
    @staticmethod
    @add_trace_span
    def run() -> str:
        main_logger.info("Start Strategy.run")
        return "Strategy called"
