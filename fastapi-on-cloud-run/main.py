from fastapi import FastAPI, Request
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from domain.strategy import Strategy
from tracing import init_trace, add_trace_span
from custom_loggers import (
    main_logger,
    env_name_context,
)

# Need to change `staging` or `production` to add spans
env = "development"
env_name_context.set(env)
init_trace(environment=env)

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)


@add_trace_span
@app.get("/")
def get_root(request: Request):
    main_logger.info(
        "Start get_root",
        additional={"http-headers": request.headers.get("user-agent")}
    )
    result = Strategy().run()
    return {"strategy-result": result}
