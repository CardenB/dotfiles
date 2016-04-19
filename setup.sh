#!/bin/sh

# Setup .vimrc:

# Save the current working directory to return later
CWD=$(echo $PWD)

# Enter the directory of this script and call pwd to get the absolute path.
# Store this in the DIR variable.
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# Move to the directory of this script.
cd $DIR
# Copy the dotfiles in this directory to the proper location.
# Copy the .vimrc in this directory to the home directory.
cp dot_vimrc ~/.vimrc
# Copy the .vim folder to the home directory
cp -r dot_vim ~/.vim
# Copy the .bashrc in this directory to the home directory.
cp dot_bashrc ~/.bashrc
# Copy the .tmux.conf in this directory to the home directory to configure tmux.
cp dot_tmux_dot_conf ~/.tmux.conf

# Return to the original directory.
cd $CWD

# Install Vundle, a vim plugin manager.
git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim

# Install Vundle plugins.
vim +PluginInstall +qall

# Install TPM, a tmux plugin manager.
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
# Source config files
source ~/.vimrc
source ~/.bashrc
tmux source ~/.tmux.conf

