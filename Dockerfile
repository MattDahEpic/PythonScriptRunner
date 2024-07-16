# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

################################################################################
# Pick a base image to serve as the foundation for the other build stages in
# this file.
FROM python:3.12-bookworm

ENV TZ="Etc/UTC"
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1

# Create a non-privileged user that the app will run under.
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser
USER appuser

# Where to link the client apps into
VOLUME /pythonapps

# Copy the executable from the "build" stage.
WORKDIR /app
COPY --chown=appuser . .
RUN ["chmod", "+x", "/app/run.sh"]

# Create base venv and install requirements
RUN python -m venv .venv && .venv/bin/python -m pip install -r requirements.txt

# What the container should run when it is started.
ENTRYPOINT /app/run.sh

