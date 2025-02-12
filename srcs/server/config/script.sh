#!/bin/bash

set -e

if ! nvm install 22 2>/dev/null; then
    if [ ! -d "$HOME/.nvm" ]; then
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
    fi

    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" 

    nvm install 22
    nvm use 22

    echo "Rebooting the system..."
    sudo reboot
fi

# TODO : - add installing the dependencies of the container

exec "$@"
