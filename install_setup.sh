#!/usr/bin/env bash

# Source bash common
source ci/bash_common.sh

# Check python version
USER_PYTHON_VERSION=""
PYTHON_PATH_CMD=$(command -v python)
PYTHON_PATH = ${PYTHON_PATH:=$PYTHON_PATH_CMD}
PYTHON_VERSION="3.8.10"
while :
do
  PYTHON_VERSION_CMD=$(${PYTHON_PATH} --version)
  successCheck "Python path search"
  USER_PYTHON_VERSION=${PYTHON_VERSION_CMD#* }
  if [ ${USER_PYTHON_VERSION} == ${PYTHON_VERSION} ];
  then
    break
  fi
  echo -e "${YELLOW}Your active python version is ${USER_PYTHON_VERSION} not ${PYTHON_VERSION}"
  echo -e "Your correct python installation might be located near:\n    ${NC}${PYTHON_PATH}"
  echo -e "${YELLOW}If installation can't be found, install Python from website"
  echo -e "${NC}Enter full correct python path to continue: "
  read PYTHON_PATH
done

# Nuke old virtual env
rm -rf .venv
${PYTHON_PATH} -m venv .venv;
successCheck "Virtual environment installation"

# Activate virtual environment
activateVenv

# Upgrade pip and install requirements
python -m pip install --upgrade pip
successCheck "Pip installation"
pip install -r requirements.txt
successCheck "Required package installation"

# Custom pip installation
if [ $OSTYPE != 'msys' ];
then
  pip install setuptools<58.0
  pip install pybluez==0.23
  # don't check for success, it's fine if we can't install pybluez
  # successCheck "Custom package installation"
fi

# Install pre-commit
pre-commit install
successCheck "Pre-commit installation"

# End script with user input
read -p "Full Installation Success! Press Enter Key to Complete..."
