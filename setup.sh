#!/bin/sh
ansible-playbook setup.yml --ask-sudo-pass

# Do vim vundle setup here, because it can't be done in an ansible playbook.

# Clean unused plugins with vundle.
# Append ! to PluginClean to auto-approve removal.
# +qall keeps vim from opening a session to display status of plugin clean.
vim  +qall +PluginClean!
# Install Vundle plugins.
# +qall keeps vim from opening a session to display status of plugin install.
vim  +qall +PluginInstall

# Source relevant files.
. ./source.sh
