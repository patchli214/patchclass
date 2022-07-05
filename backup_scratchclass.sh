#!/bin/bash
cd /data/db/bk
DATE=`date +%Y-%m-%d_%H_%M_%S`
FILENAME2="backup_PatchClass_${DATE}"
mongodump -d PatchClass -o ./
zip ./"${FILENAME2}.zip" -r  ./PatchClass
rm -rf ./PatchClass
scp -P 22 ./${FILENAME2}.zip  ubuntu@172.21.0.14:/data/db/bk/${FILENAME2}.zip
