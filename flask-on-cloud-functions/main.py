from flask import Flask, Request, request
from opentelemetry.instrumentation.flask import FlaskInstrumentor

from tracing import init_trace, add_trace_span, get_tracer
from custom_loggers import main_logger as logger, env_name_context

env = "production"
init_trace(environment=env)
env_name_context.set(env)
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)


@add_trace_span
def handler(_: Request):
    """
    Entry point for Cloud Functions
    """
    logger.info("Start main", additional={"key": "value"})

    tracer = get_tracer()
    with tracer.start_as_current_span("first"):
        logger.info("in first")
        with tracer.start_as_current_span("second"):
            logger.info("in secord")

    with tracer.start_as_current_span("third"):
        logger.info("in third")

    return {"message": "Hello World!!"}


@app.route("/")
def main():
    return handler(request)


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=80)
