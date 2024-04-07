#!/bin/sh

# pip3 install mysql-connector-python
# pip3 install tqdm
# pip3 install openpyxl
# pip3 install pika
# pip3 install treelib

#cd ../internal_server/bot/financial_sales/knowledge_base/
#python3 knowledge_embedding.py
#cd ../../../../credit_voice_service/

GREP_PROCESS1="python manage.py"
##################### restart server #############################
PID_RANK=`ps -ef|grep "$GREP_PROCESS1"|grep -v grep|awk '{print $2}'|xargs`
if [  "$PID_RANK" != "" ];then
    echo "-----Force kill current server process"
    kill -9 $PID_RANK
fi


nohup python manage.py runserver 0.0.0.0:8090 > run.log 2>&1 &
