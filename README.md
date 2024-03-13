This is a git repo for all my important dotfiles.

Run the setup.sh script in this directory to copy everything to the proper
location.

Warning, may overwrite files. Make sure you know what setup.sh does before
running it.

com.googlecode.iterm2.plist is an iTerm2 configuration profile. Load this
using the iTerm2 preferences GUI. iTerm2 is a terminal app for OS X.

To allow for tmux copy/paste to work over ssh, ssh like so:
`ssh [username]@[ip_addr] -t 'tmux new-session -A -s [session_name]'`
This command will cause tmux to run as if local which allows iterm2 to interact
with the tmux paste buffer! Also, the tmux command used will start a session
with the given name or simply attach to that session if it already exists. This
can also be found in the bashrc.

## New Setup Process

From now on, install ansible, then invoke the ansible installation path, via
`./setup.sh`.
