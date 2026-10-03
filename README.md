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

## Poppy workspace prompt

When the current directory is under `~/workspaces/<name>`, the Bash prompt
includes a colored `[poppy:<name>]` badge. The badge disappears outside a
Poppy workspace. Vim shows the same badge and color in its status line, while
tmux automatically titles the current pane `poppy:<name>`.

Workspace names are mapped deterministically onto the Solarized accent
palette. To override a mapping, edit
`roles/dotfiles/files/poppy-workspace-colors.conf`:

```
cruise3=green
evalviz=violet
```

Supported colors are `yellow`, `orange`, `red`, `magenta`, `violet`, `blue`,
`cyan`, and `green`. Apply the shell configuration with:

```
ansible-playbook setup.yml --tags dotfiles
```


## Python Packages

Python packages are now installed in a virtual environment.
It is expected that you activate the venv each session.

```
. ~/.local/.venv/bin/activate
```

## Pi

`roles/pi` installs the [pi coding agent](https://github.com/earendil-works/pi)
through Volta (with Node 22) and deploys its configuration to `~/.pi/agent`:

- `settings.json`: packages, default model, and vim mode via `pi-vim`. Pi
  installs any listed package that is missing the next time it starts.
- `settings-extensions.json`: the powerbar statusline layout.
- `session-pulse` extension: session summary and workspace digest segments.
- `terminal-title` extension: drops the `π - ` prefix from terminal and tmux
  pane titles.

With `cruise: yes` (`cruise.yml`), it also deploys the `poppy-status`
extension and `~/.local/bin/auth-status` for the Poppy workspace and auth
statusline segments. Elsewhere those segments stay hidden.

```
ansible-playbook setup.yml --tags pi
ansible-playbook cruise.yml --tags pi
```

Credentials, sessions, caches, and MCP servers stay local to each machine.
