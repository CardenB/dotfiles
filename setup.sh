#!/bin/sh

# Setup specific to MacOS
if [[ "$OSTYPE" == "darwin"* ]]; then
  # Install latest homebrew.
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

  # Use homebrew to install ansible
  brew install ansible
elif [[ "$OSTYPE" == "linux-gnu" ]]; then
  sudo apt-get install ansible
fi
ansible-playbook setup.yml
