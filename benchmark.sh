exec ping -c 2 127.0.0.1 > /dev/null 2>&1 &
PID="$!"
STARTTIME=""
while kill -0 $PID >/dev/null 2>&1
do
	STARTTIME=`ps -ef | grep $PID | cut -d ' ' -f8`;
	ps --no-headers -o '%cpu,%mem' -p "$PID";
done
ENDTIME=`date +%H:%M`
echo $STARTTIME
echo $ENDTIME
exit 0
