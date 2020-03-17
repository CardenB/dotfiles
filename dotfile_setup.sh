#!/bin/bash

# Setup .vimrc:

# Save the current working directory to return later
CWD=$(echo $PWD)

# Enter the directory of this script and call pwd to get the absolute path.
# Store this in the DIR variable.
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# Move to the directory of this script.
cd $DIR

# Copy dotfiles in this directory to the proper location.
# Do not symlink these files, as it doesn't work.
cp -r ./dotfiles/. ~/

# Return to the original directory.
cd $CWD

# Install Vundle, a vim plugin manager.
VUNDLE_DIR=~/.vim/bundle/Vundle.vim
if [ ! -d $VUNDLE_DIR ]
then
  git clone https://github.com/VundleVim/Vundle.vim.git $VUNDLE_DIR
else
  echo Skipping vundle clone, already exists at $VUNDLE_DIR
fi

# Install TPM, a tmux plugin manager.
# When you open tmux, use `prefix + I` to fetch the plugins and install.
TMUX_PLUGIN_DIR=~/.tmux/plugins/tpm
if [ ! -d $TMUX_PLUGIN_DIR ]
then
  git clone https://github.com/tmux-plugins/tpm
else
  echo Tmux plugin clone, already exists at $TMUX_PLUGIN_DIR
fi
