#!/bin/bash

cd $( dirname $0 )

latest=$( ls output-virtualbox-iso/*.ova | sort | tail -n1 )

date=$( date --rfc-3339=date )
desc=$( git describe )
relpath="camisole-$desc-$date.ova"
path="/home/camisole/www/ova/$relpath"

scp "$latest" "camisole@prologin.org:$path"

ssh camisole@prologin.org chmod 644 "$path"
ssh camisole@prologin.org ln -sf "./$relpath" /home/camisole/www/ova/camisole-latest.ova
