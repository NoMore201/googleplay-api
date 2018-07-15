#!/bin/bash

REPO_SRC="https://github.com/yeriomin/play-store-api"
REPO_LOCAL="/tmp/psapi"
RES_DIR="${REPO_LOCAL}/src/main/resources"

DEVS_FILE="./gpapi/device.properties"

command -v git >/dev/null 2>&1 || { echo "git not installed"; exit 1; }

if [ ! -d "./gpapi" ]; then
        echo "No gpapi dir found! Make sure you're in googleplay-api root dir"
        exit 1
fi

echo "==> Cloning play-store-api repo into $REPO_LOCAL"
git clone $REPO_SRC $REPO_LOCAL &>/dev/null

# clean device.properties file
echo "" > $DEVS_FILE

for dev in `ls $RES_DIR`; do
        FILE="$RES_DIR/$dev"
        NAME=`echo $dev | sed -e "s/device-\(.*\).properties/\1/"`
        echo "==> appending device data for $NAME"
        echo "[$NAME]" >> $DEVS_FILE
        cat $FILE >> $DEVS_FILE
        echo "" >> $DEVS_FILE
done

# cleanup
echo "==> Cleanup"
rm -rf $REPO_LOCAL
