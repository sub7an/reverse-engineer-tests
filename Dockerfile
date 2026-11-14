# The upload app in a container.
#
#   docker build -t reverse-engineer-tests .
#   docker run --rm -p 8765:8765 reverse-engineer-tests
#
# then open http://127.0.0.1:8765
#
# The app has no sign-in and no rate limit. To publish it on the internet, put
# it behind a proxy or platform that adds both, and check that you are allowed
# to process the papers people will upload.
FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends poppler-utils \
 && rm -rf /var/lib/apt/lists/* \
 && useradd --create-home app

COPY skills/reverse-engineer-tests /app
USER app
WORKDIR /app/scripts

ENV PORT=8765 PYTHONUNBUFFERED=1
EXPOSE 8765
CMD ["python3", "serve.py", "--host", "0.0.0.0"]
