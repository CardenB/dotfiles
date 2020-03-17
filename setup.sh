#!/bin/sh
ansible-playbook setup_playbook.yml --ask-sudo-pass

# Do vim vundle setup here, because it can't be done in an ansible playbook.

# Clean unused plugins with vundle.
# Append ! to PluginClean to auto-approve removal.
# +qall keeps vim from opening a session to display status of plugin clean.
vim  +qall +PluginClean!
# Install Vundle plugins.
# +qall keeps vim from opening a session to display status of plugin install.
vim  +qall +PluginInstall

# Source config files for them to take effect.
# Use `.` instead of `source` here because `source` is not found by bash.
. ~/.bashrc
tmux source ~/.tmux.conf
