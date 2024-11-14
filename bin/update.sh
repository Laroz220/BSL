#!/bin/bash

echo -e "Looking for updates.. Please wait!"

update_dir=$C_HOME/sys/software/update
mkdir -p $update_dir; cd $update_dir

git clone https://github.com/Laroz220/BSL.git 2>/dev/null && cd BSL
source update/setup.sh

rm -rf $update_dir



