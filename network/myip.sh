#!/bin/bash

# CREATE TABLE ips (machine VARCHAR(60), date TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc'), ip INET);  

remote=$(cat /etc/myip.conf | grep remote | cut -d= -f2)
machine=$(cat /etc/myip.conf | grep machine | cut -d= -f2)
postgres_user=$(cat /etc/myip.conf | grep postgres_user | cut -d= -f2)

ip=$(upnpc -s \
    | grep ExternalIPAddress \
    | cut -d ' ' -f3)

last_ip=$(ssh $remote "psql -t --pset=border=0 -U $postgres_user -c \"SELECT ip FROM ips WHERE machine='$machine' ORDER BY date DESC LIMIT 1;\"")

echo \"$last_ip\" \"$ip\"

if [ "$last_ip" == "$ip" ]
then
	echo Not updating $remote because ip did not change
else
	echo Saving new ip $ip at remote $remote for machine $machine
	ssh $remote "psql -U $postgres_user -c \"INSERT INTO ips(machine, ip) VALUES('$machine', '$ip');\"" >/dev/null
fi
