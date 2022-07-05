sudo pkill -f uwsgi -9
cd /data/go2
/data/uwsgi-2.0.18/uwsgi --socket go2.sock --module go2.wsgi --chmod-socket=666 &
disown
cd /data/PatchClass
/data/uwsgi-2.0.18/uwsgi --socket PatchClass.sock --module PatchClass.wsgi --chmod-socket=666 &
disown
cd /data/gotest
/data/uwsgi-2.0.18/uwsgi --socket go2.sock --module go2.wsgi --chmod-socket=666 &
disown
