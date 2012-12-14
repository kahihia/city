#!/bin/bash
set -e
LOGFILE=/root/cityfusion-hg/cityfusion.log
LOGDIR=$(dirname $LOGFILE)
NUM_WORKERS=3
# user/group to run as
USER=root
GROUP=root
ADDRESS=127.0.0.1:8001
cd /root/cityfusion-hg/alpha
source /root/cityfusion-hg/bin/activate
test -d $LOGDIR || mkdir -p $LOGDIR
exec ../bin/gunicorn_django -w $NUM_WORKERS --bind=$ADDRESS  \
  --user=$USER --group=$GROUP --log-level=debug \
  --log-file=$LOGFILE 2>>$LOGFILE

