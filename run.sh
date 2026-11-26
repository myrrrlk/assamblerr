#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
case "${1:-test}" in
    assembler|interpreter)
        command=$1
        shift
        exec python3 "src/$command.py" "$@"
        ;;
    test)
        if [ "$#" -gt 0 ]; then shift; fi
        exec python3 -m unittest discover -s tests -v "$@"
        ;;
    *)
        echo "Usage: $0 [test|assembler|interpreter] [arguments...]" >&2
        exit 2
        ;;
esac
