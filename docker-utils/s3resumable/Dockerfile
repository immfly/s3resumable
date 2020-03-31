ARG PYTHONVERSION=3.7.7
FROM python:${PYTHONVERSION}-alpine3.11

ENV PYTHONBUFFERED 1
ARG uid=1000
ARG gid=1000
ARG PYTHONBIN
ENV PYTHONBIN=${PYTHONBIN:-python3}

# Install system dependencies
RUN apk --update add --no-cache gcc bash $PYTHONBIN-dev build-base \
    && rm -rf /var/cache/apk/*

# Create user and group
RUN addgroup -S app --gid $gid \
    && adduser -S app -G app --uid $uid

# Create application directory
RUN set -ex && mkdir /app && chown app:app /app

USER app
ADD --chown=app:app . /app
ADD ./docker-utils/s3resumable/docker-entrypoint.sh /usr/local/bin/entrypoint
WORKDIR /app
ENV PATH /home/app/.local/bin:$PATH

# Install python requirements
RUN $PYTHONBIN -m pip install --user pipenv
RUN pipenv --python $PYTHONBIN install -e .[dev]

ENTRYPOINT ["entrypoint"]
CMD ["s3resumable"]
