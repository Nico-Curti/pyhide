#!/bin/bash

scriptdir=$(dirname $(readlink /proc/$$/fd/255))
pushd "$scriptdir" > /dev/null

pyhide --input ./hello_world.py --variable --function --class --num --pkg --str --op
pyhide --input ./simple_func.py --variable --function --class --num --pkg --str --op
pyhide --input ./simple_pkg.py --variable --function --class --num --pkg --str --op
pyhide --input ./simple_class.py --variable --function --class --num --pkg --str --op

popd > /dev/null
