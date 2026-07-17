# /bin/zsh

set -e
tmux new -d -s notes
tmux new -d -s general
tmux new -d -s workers
tmux new -d -s cloud-sql-proxy
tmux attach -t general

