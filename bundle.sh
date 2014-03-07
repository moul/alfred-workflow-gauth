#!/bin/bash

# This script will create the Alfred workflow file and optionally it will install it.
# To install it, pass the argument "-i" or "--install", e.g.
# bundle.sh --install

echo "Creating Google Authenticator workflow file..."

WORKFLOW_FILE=Google\ Authenticator.alfredworkflow
if [ -f "$WORKFLOW_FILE" ]; then
	echo "Removing previous workflow..."
    rm "$WORKFLOW_FILE"
fi

echo "Bundling it..."
cd src && zip -r "../$WORKFLOW_FILE" * -x "*.DS_Store" && cd ..

while test $# -gt 0
do
    case "$1" in
        --install | -i)
			echo "Installing $WORKFLOW_FILE..."
			open "$WORKFLOW_FILE"
            ;;
    esac
    shift
done

echo "$WORKFLOW_FILE is ready!"
