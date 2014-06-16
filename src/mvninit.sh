#!/bin/bash
# init script for `mvn tomcat7:run`
 
 
MAVEN_OPTS_CLI="-DXms256m -DXmx1024m -Dorg.apache.jasper.compiler.Parser.STRICT_QUOTE_ESCAPING=false -Djava.awt.headless=true -Dmaven.compiler.useIncrementalCompilation=false -D-noverify"
JAVA_HOME="/usr/lib/jvm/java-8-oracle/jre"
M2_HOME="/usr"
MAVEN_REPO="/home/fenixedu/.m2/repository"
 
LOG_FILE="log/fenix.out"
PID_FILE=".run/mvn_pid"
 
JAVA="$JAVA_HOME/bin/java"
MAVEN="$M2_HOME/bin/mvn"
 
BASE_DIR="/home/fenixedu"
LOG_FILE="$BASE_DIR/$LOG_FILE"
PID_FILE="$BASE_DIR/$PID_FILE"

export JAVA_OPTS="-Xms512m -Xmx2048m"

export MAVEN_OPTS="$JAVA_OPTS  -Dorg.apache.jasper.compiler.Parser.STRICT_QUOTE_ESCAPING=false"
  
do_start(){
    if [ -f $PID_FILE ]
    then
        echo "already started (pid: `cat $PID_FILE`)"
        return 0
    fi
    do_force_start
    return 0
}

do_force_start(){
    do_stop
    cd $BASE_DIR/fenixedu-appliance-webapp
    mvn $MAVEN_OPTS_CLI tomcat7:run > $LOG_FILE 2>&1 &
    echo -n $! > $PID_FILE
 
    SUCCESS_EXPECTED="FrameworkServlet 'dispatcher': initialization completed"
    ERROR_EXPECTED="ERROR"
 
    [ ! "$?" = 0 ] && echo error && do_stop
    return 0
}
 
do_stop(){
    if [ -f $PID_FILE ]
	    then
	 
	    TIME=4
	    kill `cat $PID_FILE`
	    EXIT_STATUS=$?
	    while [ $TIME -gt 0 ] && [ ! "$EXIT_STATUS" = 0 ]
	    do
		sleep 1
		TIME=$(( $TIME - 1 ))
		kill `cat $PID_FILE`
		EXIT_STATUS=$?
	    done
	 
	    if [ $TIME = 0 ]
	    then
		kill -9 `cat $PID_FILE`
		EXIT_STATUS=$?
		rm "/home/fenixedu/fenixedu-appliance-webapp/target/tomcat" -rf
		rm "$PID_FILE"
	    fi
	 
	    if [ "$EXIT_STATUS" = 0 ]
	    then
		rm "$PID_FILE"
		echo stop
	    else
		echo error
		return 0
	    fi
    else
	echo NOT running
        return 0
    fi
}
 
do_status(){
    if [ -f $PID_FILE ]
    then
        echo "running (pid `cat $PID_FILE`)"
    else
        echo "NOT running"
        return 0
    fi
}
 
case $1 in
    start | stop | force_start | status) do_$1 ;;
    restart ) do_stop && do_start ;;
    * )
        echo "`basename $0` {start|stop|restart|status}"
        exit 4
esac
exit 0
