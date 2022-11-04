from functools import lru_cache, wraps

# https://cloud.google.com/trace/docs/setup/python-ot#import_and_configuration
from opentelemetry import trace
from opentelemetry.trace import Tracer
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.cloud_trace_propagator import (
    CloudTraceFormatPropagator,
)
from opentelemetry.instrumentation.logging import LoggingInstrumentor


# Cloud Trace へ span を送信する設定を行う
def init_trace(environment: str):
    # ログにtrace id, span idを埋め込むためのおまじない
    LoggingInstrumentor().instrument(set_logging_format=True)

    if environment not in ["staging", "production"]:
        # local環境などでtraceの設定を行うとspanを打つ際に例外が上がるのでreturnする
        return

    set_global_textmap(CloudTraceFormatPropagator())
    # Cloud Run の場合はサンプルレートが `0.1 requests per second for each container instance` となる
    # https://cloud.google.com/run/docs/trace#trace_sampling_rate
    tracer_provider = TracerProvider(
        resource=Resource.create(
            {
                "service.name": "fastapi-on-cloud-run",
                "service.environment": environment,
            }
        ),
    )
    # resource_regexは TracerProvider のresourceパラメータとして渡す任意のkey/valueを
    # Cloud Trace に表示されるSpanのラベルとして表示するために必要な設定
    # https://github.com/GoogleCloudPlatform/python-docs-samples/issues/7300#issuecomment-1164737444
    exporter = CloudTraceSpanExporter(resource_regex="service.*")
    tracer_provider.add_span_processor(
        # 下記で述べられている BatchSpanProcessor はバックグラウンドプロセスをサポートしてない Cloud Run では使用不可
        # https://cloud.google.com/trace/docs/setup/python-ot#:~:text=Cloud%20Run%20doesn%27t%20support%20background%20processes
        # そのため実行中のプロセスで span を送信する SimpleSpanProcessor を使う
        SimpleSpanProcessor(exporter)
    )
    trace.set_tracer_provider(tracer_provider)


@lru_cache(maxsize=None)
def get_tracer() -> Tracer:
    """Generate tracer instance
    メソッド単位より更に柔軟にSpanを打ちたい場合に使う

    Usage:
        from trace import get_trace

        def do_something(self):
            tracer = get_trace()
            with tracer.start_as_current_span("Do something"):
                do_something
    """

    return trace.get_tracer(__name__)


def add_trace_span(f):
    """Decorator method to add span to a method
    Reference: https://recruit.gmo.jp/engineer/jisedai/blog/gcp-cloud-trace/#anchor5

    Usage:
        from trace import add_trace_span

        @add_trace_span
        def do_something(self):
            do_something
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        tracer = get_tracer()
        with tracer.start_as_current_span(name=f.__qualname__):
            return f(*args, **kwargs)

    return wrapper


class TraceContextManager:
    @classmethod
    def __span_context(cls):
        return trace.get_current_span().get_span_context()

    @classmethod
    def get_trace_id(cls) -> str:
        # trace idはOpenTelemetryの仕様上、128 ビットの番号を表す 32 文字の 16 進数値だが
        # PythonのOpenTelemetryのpackage内だとintで管理されているので
        # パッケージ側のフォーマット関数をかませる必要がある
        return trace.format_trace_id(cls.__span_context().trace_id)
