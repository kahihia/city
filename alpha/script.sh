#!/bin/bash
set -e
LOGFILE=/root/cityfusion_redesign/cityfusion.log
LOGDIR=$(dirname $LOGFILE)
NUM_WORKERS=3
# user/group to run as
USER=root
GROUP=root
ADDRESS=127.0.0.1:8003
cd /root/cityfusion_redesign/alpha
#source ../bin/activate
test -d $LOGDIR || mkdir -p $LOGDIR
exec gunicorn_django -w $NUM_WORKERS --bind=$ADDRESS  \
  --user=$USER --group=$GROUP --log-level=debug \
  --log-file=$LOGFILE 2>>$LOGFILE

