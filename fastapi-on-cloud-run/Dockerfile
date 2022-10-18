FROM python:3.10-slim-buster

ENV APP_DIR /usr/src/app
WORKDIR $APP_DIR

ARG GROUP_ID=1100
ARG USER_ID=1100
RUN groupadd --system --gid $GROUP_ID app && \
      useradd --system --gid $GROUP_ID --create-home --uid $USER_ID app && \
      mkdir -p $APP_DIR && \
      chown app:app $APP_DIR

RUN pip install poetry
COPY poetry.toml $APP_DIR
COPY pyproject.toml $APP_DIR
COPY poetry.lock $APP_DIR
RUN poetry install --no-root

USER $USER_ID:$GROUP_ID

COPY . $APP_DIR

ENTRYPOINT ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
