#!/bin/bash

PYTHON_EGG_CACHE="/tmp/.PYTHON_EGG_CACHE_zipserver"
EXEC_USER="hejiarong"
LOG_DIR="/data/logs/zipserver"

LISTEN_IP="127.0.0.1"
BASE_PORT=8004
WORKER_COUNT=1
EXEC="/usr/bin/python2.7"
MAIN_FILE="./zipserver_gevent.py"
ARGS="1000"
STDOUT="./__gevent_wsgiserver.stdout"
DISP_NAME="gevent_wsgiserver"
PROC_SIG=${DISP_NAME}"_MdffDFEfsesf"

# Consts
RED='\e[1;91m'
GREN='\e[1;92m'
WITE='\e[1;97m'
NC='\e[0m'

# Global vailables
PROC_COUNT="0"
function count_proc()
{
    PROC_COUNT=$(ps -ef | grep $MAIN_FILE | grep $PROC_SIG | grep -vc grep)
}
function list_proc()
{
    ps -ef | grep -v grep | grep $PROC_SIG | grep --color $MAIN_FILE
}
function list_proc_pids()
{
    ps -ef | grep $MAIN_FILE | grep $PROC_SIG | grep -v grep | awk '{print $2}'
}


function start_procs()
{
    printf "Starting $DISP_NAME processes"

    sudo /usr/sbin/useradd -M -s /bin/false $EXEC_USER 1>/dev/null 2>&1
    sudo mkdir -p $LOG_DIR
    sudo chown $EXEC_USER.$EXEC_USER $LOG_DIR
    sudo chown $EXEC_USER.$EXEC_USER .
    sudo mkdir -p $PYTHON_EGG_CACHE
    sudo chmod 777 $PYTHON_EGG_CACHE

    count_proc
    if [ $PROC_COUNT \> 0 ]; then
        echo
        list_proc
        echo -e ${RED}"\n[ERROR]" ${NC}"Start $DISP_NAME failed, processes already runing."
        exit -1
    fi

    for ((PORT=$BASE_PORT; PORT<WORKER_COUNT+$BASE_PORT; PORT=PORT+1)); do
        sudo -u $EXEC_USER PYTHON_EGG_CACHE=${PYTHON_EGG_CACHE} $EXEC $MAIN_FILE $LISTEN_IP $PORT $ARGS $PROC_SIG 1>$STDOUT 2>&1 &
        echo $PORT
    done

    count_proc
    while [ ${PROC_COUNT} -ne $WORKER_COUNT ]; do
        printf "."
        sleep 0.2
        count_proc
    done

    echo -e ${GREN}"\n[OK]" ${NC}"$DISP_NAME start succesfully."
}

function stop_procs()
{
    printf "Stoping $DISP_NAME"
    count_proc
    if [ ${PROC_COUNT} -eq 0 ]; then
        echo -e ${RED}"\n[ERROR]" ${NC}"$DISP_NAME process not found."
        exit -1
    fi
    
    kill -SIGKILL $(list_proc_pids)
    count_proc
    while [ ${PROC_COUNT} -ne 0 ]; do
        printf "."
        sleep 0.2
        count_proc
    done
    echo -e ${GREN}"\n[OK]" ${NC}"$DISP_NAME stop succesfully."
}

function status_procs()
{
    count_proc
    echo -e ${RED}${PROC_COUNT}${NC} "$DISP_NAME processes runing."        
}

MODE=${1}
case ${MODE} in
    "start")
        start_procs
        ;;

    "stop")
        stop_procs
        ;;

    "restart")
        stop_procs
        start_procs
        ;;

    "status")
        status_procs
        ;;
    
    *)
        # usage
        echo -e "\nUsage: $0 {start|stop|restart|status}"
        echo -e ${WITE}" start   "${NC}"Start $DISP_NAME processes."
        echo -e ${WITE}" stop    "${NC}"Kill all $DISP_NAME processes."
        echo -e ${WITE}" restart "${NC}"Kill all $DISP_NAME processes and start again."
        echo -e ${WITE}" status  "${NC}"Show $DISP_NAME processes status.\n"
        exit 1
        ;;
esac

