#!/usr/bin/sh

pid=$(ps ax | grep "./server.py" | awk '{ print $1 }' | tail -1)

kill $pid

git pull

nohup ./server.py &

