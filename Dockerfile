ARG PYTHON_IMAGE
ARG PYTHON_IMAGE_VERSION

FROM ${PYTHON_IMAGE}:${PYTHON_IMAGE_VERSION}

ARG POETRY_VERSION
ARG ENVIRONMENT

WORKDIR /opt/teashop

COPY pyproject.toml .
COPY README.md .
COPY teashop/ teashop/
COPY tests/ tests/

RUN pip install --upgrade pip
RUN if [ "${ENVIRONMENT}" = "development" ]; then \
        pip install "poetry==${POETRY_VERSION}" && \
        poetry config virtualenvs.create false && \
        poetry install; \
    elif [ "${ENVIRONMENT}" = "production" ]; then \
        pip install -e .; \
    else \
        echo "Invalid environment specified: '${POETRY_VERSION}'"; \
        exit 1; \
    fi