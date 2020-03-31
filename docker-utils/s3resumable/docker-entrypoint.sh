#!/bin/bash
set -e

launch_s3resumable() {
  pipenv run s3resumable ${@}
}

launch_qa() {
  pipenv run pylint s3resumable
  pipenv run coverage run --source=s3resumable -m pytest
  pipenv run coverage report -m 
}

case $1 in
  "s3resumable")
    shift
    launch_s3resumable "${@}"
    ;;
  "qa")
    launch_qa ;;
  *)
    exec "${@}" ;;
esac
