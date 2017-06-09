#!/bin/bash

# Setup .vimrc:

# Save the current working directory to return later
CWD=$(echo $PWD)

# Enter the directory of this script and call pwd to get the absolute path.
# Store this in the DIR variable.
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# Move to the directory of this script.
cd $DIR
# Symlink dotfiles in this directory to the proper location.
# This will allow you to edit files in a single place.
# -s is arg for creating symlink, -f is for creating and updating.
ln -sf ./dot_vimrc ~/.vimrc
ln -sf ./dot_bashrc ~/.bashrc
ln -sf ./dot_tmux_dot_conf ~/.tmux.conf
ln -sf ./dot_ctags ~/.ctags

# Return to the original directory.
cd $CWD

# Install Vundle, a vim plugin manager.
git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim

# Install Vundle plugins.
vim +PluginInstall +qall

# Install TPM, a tmux plugin manager.
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
# Source config files
source ~/.bashrc
tmux source ~/.tmux.conf

