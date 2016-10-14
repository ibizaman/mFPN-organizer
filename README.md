Tools to organize various files.

# network/myip.sh

Store current external ip address into a postgres db in a remote host.
Does not rely on external service to know the external ip address.

1. Create db, role and table in remote postgres db (see myip.sh comment for schema)
2. Add remote host login info to .ssh/config
3. cp myip.conf.template /etc/myip.conf
4. Set cron job to run myip.sh regularly

# storage/lvm.py

Prints summary view of lvm physical volumes, volume groups and logical
volumes along with raid information.
