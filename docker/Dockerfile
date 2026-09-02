# Ālaya. Core only — the store, the stream, the console, 共業.
#
# The eye and the ear are deliberately absent from this image. Camera and
# microphone access does not cross the Docker VM boundary on macOS, and a
# faculty that reports itself present and then delivers nothing is worse than
# one that is honestly dormant. In a container all five senses take injection;
# 無心位 for the two that would otherwise have devices.
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY alaya/ ./alaya/
COPY config/ ./config/
COPY examples/ ./examples/
COPY mcp_server/ ./mcp_server/

ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "-m", "alaya", "--no-eye", "--no-ear"]
