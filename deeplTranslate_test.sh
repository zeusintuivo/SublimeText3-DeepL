#!/usr/bin/env bash
#!/bin/bash
#
# @author Zeus Intuivo <zeus@intuivo.com>
#

declare python_exec='python'
if [[ ! -z "${1}" ]] ; then
{
    if [[ "${1}" = *"--h"*  ]] ; then
    {
        cat <<EOF

   How to call

 ./deeplTranslate_test.sh   <---  runs default python

 ./deeplTranslate_test.sh python3     <---- changes to python3 as executable

EOF
        exit 0;
    }
    else
    {
        python_exec="${1}"
    }
    fi
}
fi
nodemon --watch test/deeplTranslate_test.py \
        --watch libs/process_strings.py  \
        --watch core/translate.py --exec "${python_exec}" test/deeplTranslate_test.py
