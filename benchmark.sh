#!/bin/bash

exec ffmpeg -i /home/liraop/Downloads/KGLW-gammaknife-360.mp4 /home/liraop/Downloads/kglw-360.avi > /dev/null 2>&1 &
PID="$!"
total_cpu=0.0
total_mem=0.0
samples=0
while kill -0 $PID >/dev/null 2>&1
do
	STARTTIME=`ps -o lstart= -p $PID | cut -d" " -f4`
	OUT=`ps --no-headers -o '%cpu,%mem' -p "$PID" | cut -d" " -f1-`
	for i in $OUT
	do
		read CPU MEM <<< $OUT
		total_cpu=`python -c "print($total_cpu+$CPU)"`
		total_mem=`python -c "print($total_mem+$MEM)"`
		samples=$((samples+1))
	done
done
total_cpu=`python -c "print($total_cpu/$samples)"`
total_mem=`python -c "print($total_mem/$samples)"`
ENDTIME=`date +%T`
FORMATED_ENDTIME=`echo $ENDTIME  | awk -F: '{ print ($1 * 3600) + ($2 * 60) + $3 }'`
FORMATED_STARTTIME=`echo $STARTTIME | awk -F: '{ print ($1 * 3600) + ($2 * 60) + $3 }'`
TOTALTIME="Tempo (segs): $(($FORMATED_ENDTIME-$FORMATED_STARTTIME))"

echo $total_cpu
echo $total_mem
echo $TOTALTIME
exit 0
