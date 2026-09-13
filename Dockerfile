FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /workspace

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN python -m pip install --upgrade pip && python -m pip install '.[quantum]'

COPY configs ./configs
COPY scripts ./scripts

RUN useradd --create-home --uid 10001 researcher && \
    mkdir -p /workspace/data /workspace/artifacts/public /workspace/reports && \
    chown -R researcher:researcher /workspace

USER researcher

ENTRYPOINT ["qheart"]
CMD ["--help"]
