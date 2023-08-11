ARG IMAGE_NAME
ARG IMAGE_VERSION

FROM ${IMAGE_NAME}:${IMAGE_VERSION}

ARG POETRY_VERSION

RUN pip install --upgrade pip setuptools
RUN pip install "poetry==${POETRY_VERSION}"

WORKDIR /opt/pode

COPY pyproject.toml .
RUN poetry config virtualenvs.create false
RUN poetry install

COPY README.md .
COPY pytest.ini .
COPY teashop/teashop teashop
COPY tests tests
