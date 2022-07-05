#!/bin/bash
cd /data/db/bk
FILENAME=$(ls -tr | tail -1)
unzip ${FILENAME}
mongorestore --drop -d PatchClass PatchClass
rm -rf ./PatchClass
