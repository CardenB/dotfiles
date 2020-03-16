#!/bin/bash
# Some place for a temp vim installation.
VIM_REPO=/tmp/vim_repo/

# Make sure the temp directory is clean.
if [ -d $VIM_REPO ]
then
  echo temp directory name collision. Cannot proceed.
  exit 1
fi

# Clone to vim repo so we can configure and install.
git clone https://github.com/vim/vim.git $VIM_REPO

pushd $VIM_REPO

# Configure vim install from source to be awesome.
./configure --with-features=huge\
            --enable-multibyte\
            --enable-rubyinterp=yes\
            --enable-python3interp=yes\
            --with-python3-config-dir=$(python3-config --configdir)\
            --enable-cscope

# Install with checkinstall so that we can easily uninstall.
sudo checkinstall -y

popd
# Clean up the vim repo.
sudo rm -rf $VIM_REPO
