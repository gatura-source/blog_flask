#!/bin/bash

function startapp(){
    local default_host="127.0.0.1"
    local default_port="5000"
    local host=${1:-$default_host}
    local port=${2:-$default_port}

    echo -e "Activating Virtual Environment"
    source .venv/bin/activate  # Adjust to your virtual environment path

    echo -e "Setting up the environment variables"
    export FLASK_APP=app
    export FLASK_DEBUG=1
    export FLASK_ENV=development

    echo -e "\nStarting Application"
    echo -e "HOST: $host\tPORT: $port\n"
    flask run --host="$host" --port="$port"
}
startapp "$1" "$2"
