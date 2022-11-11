FROM python:3.11-slim AS python-snippets

ARG PIPX_VERSION=1.0.0
ARG POETRY_VERSION=1.1.12

RUN apt update

# Install poetry and set up path
ENV PIPX_BIN_DIR=/opt/pipx/bin
ENV PIPX_HOME=/opt/pipx/home
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH=/opt/pipx/bin:/app/.venv/bin:$PATH

RUN pip install --upgrade pip setuptools
RUN pip install pipx==$PIPX_VERSION
RUN pipx install poetry==$POETRY_VERSION

# Set working directory
WORKDIR /app

# Install project dependecies
COPY pyproject.toml poetry.lock ./
RUN poetry install

# Copy required project files
COPY snippets snippets
COPY README.md ./

# Keep container alive
ENTRYPOINT ["tail"]
CMD ["-f","/dev/null"]
