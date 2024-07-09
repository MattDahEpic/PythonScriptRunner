service cron start

cd /app
.venv/bin/python setup.py

# Spin forever to allow cron to run
while true
do
    sleep 1
done