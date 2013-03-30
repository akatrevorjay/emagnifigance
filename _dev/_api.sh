#!/bin/bash -e

#BASHISM_DEBUG=1
#BASHISM_COLORS=1

#args="$@"
#set --

#. ./bin/env
shopt -s extglob

function api {
    local url="$1"
    local base="" opts="" params=""
    case "$url" in
        !(http://*))
            base="https://emag-api.localhostsolutions.com"
            opts+="--verify no " ;;&
        !(/*))
            base+="/" ;;&
        !(*api/v1/*))
            base+="api/v1" ;;&
        !(/*))
            base+="/" ;;&
        #!(*?*))
        #    url="/$url"
        #    ;;&

        !(username=*))
            params+="&username=trevorj&api_key=a8fc08f0adcb845c6f6907c35aea03d44d38ec4d" ;;&
    esac

    opts+="--json "

    # Replace first char with ?
    [[ -n "$params" && $url = *\?* ]] && params="&${params:1}" || params="?${params:1}"

    #debug http "$base$url" "${@:2}"
    echo DEBUG: http $opts "$base$url$params" "${@:2}"
    http $opts "$base$url$params" "${@:2}"
}

api "$@"
