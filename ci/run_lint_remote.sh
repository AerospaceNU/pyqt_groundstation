#!/usr/bin/env bash

# Source bash common
source ci/bash_common.sh

# Run linting
runBlack
runIsort
#runFlake8
#runMypy
