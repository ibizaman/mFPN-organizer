Various tools to automate tasks.

# Install

Use venv and pip:

```
sudo pacman -S python-pip
sudo pip install -U virtualenv
virtualenv .venv
.venv/bin/pip install -e '.[dev,test]'
```

# network/myip.py

Store current external ip address into a godaddy A record, or update the
record.

# network/myip.sh

[DEPRECATED]

Store current external ip address into a postgres db in a remote host.
Does not rely on external service to know the external ip address.

1. Create db, role and table in remote postgres db (see myip.sh comment for schema)
2. Add remote host login info to .ssh/config
3. cp myip.conf.template /etc/myip.conf
4. Set cron job to run myip.sh regularly

# network/ports.py

Enforce a list of port forwarding listed in a config file using the
external command `upnpc`.

# storage/lvm.py

Prints summary view of lvm physical volumes, volume groups and logical
volumes along with raid information, mounts and devices.

Example output:
```
 Raid                    |   LVM                            |   Mounts                                                  |   Devices                          
                         |                                  |                                                           |                                    
/dev/md0    [raid1] 2/2  |  mirror 699.87 GiB (99%)         |  /dev/mapper/mirror-albums    ext3     253.83 GiB  (69%)  |  /dev/md0 Linux Software RAID Array
  /dev/sdb1              |   P  /dev/md0 699.87 GiB (99%)   |    /srv/pictures                                          |  /dev/sda ATA WDC WD25EZRS-00J     
  /dev/sdi1              |   L  albums   258.0 GiB  (69%)   |  /dev/mapper/mirror-backups   ext3     330.6 GiB   (85%)  |     /dev/sda1 1000.0 GiB           
                         |   L  backups  336.0 GiB  (85%)   |    /srv/backups                                           |     /dev/sda2 1.3 TiB              
                         |   L  music    100.0 GiB  (18%)   |  /dev/mapper/mirror-music     ext2     98.43 GiB   (18%)  |  /dev/sdb ATA WDC WD20EARS-07M     
                         |   L  torrents 5.0 GiB    (55%)   |    /srv/nfs/music                                         |   R  /dev/sdb1 700.0 GiB           
                         |  strip 1.2 TiB (32%)             |  /dev/mapper/mirror-torrents  ext3     4.8 GiB     (55%)  |   L  /dev/sdb2 1.14 TiB            
                         |   P  /dev/sdf1 298.09 GiB (0%)   |    /srv/torrents                                          |  /dev/sdc Intenso Rainbow          
                         |   P  /dev/sdg2 931.51 GiB (43%)  |  /dev/mapper/strip-home       ext3     255.8 GiB   (80%)  |     /dev/sdc1 7.44 GiB             
                         |   L  home      260.0 GiB  (80%)  |    /home                                                  |  /dev/sdd ATA WDC WD20EZRZ-00Z     
                         |   L  opt       50.0 GiB   (58%)  |  /dev/mapper/strip-opt        ext3     49.09 GiB   (58%)  |     /dev/sdd1 1.82 TiB             
                         |   L  root      20.0 GiB   (51%)  |    /opt                                                   |  /dev/sde ATA WDC WD20EZRZ-00Z     
                         |   L  swap      2.0 GiB           |  /dev/mapper/strip-root       ext3     19.56 GiB   (51%)  |     /dev/sde1 1.82 TiB             
                         |   L  var       70.0 GiB   (89%)  |    /                                                      |  /dev/sdf ATA WDC WD3200BEVT-7     
                         |  strip2 3.64 TiB (96%)           |  /dev/mapper/strip-var        ext3     68.78 GiB   (89%)  |   L  /dev/sdf1 298.09 GiB          
                         |   P  /dev/sdb2 1.14 TiB  (100%)  |    /var                                                   |  /dev/sdg ATA ST31000528AS         
                         |   P  /dev/sdh1 300.0 GiB (77%)   |  /dev/mapper/strip2-downloads ext3     49.09 GiB   (48%)  |      /dev/sdg1 1.0 MiB             
                         |   P  /dev/sdh2 1.07 TiB  (100%)  |    /srv/downloads                                         |   L  /dev/sdg2 931.51 GiB          
                         |   P  /dev/sdi2 1.14 TiB  (95%)   |  /dev/mapper/strip2-movies    ext3     2.43 TiB    (62%)  |  /dev/sdh ATA SAMSUNG HD154UI      
                         |   L  downloads 50.0 GiB  (48%)   |    /srv/movies                                            |   L  /dev/sdh1 300.0 GiB           
                         |   L  movies    2.46 TiB  (62%)   |  /dev/mapper/strip2-series    ext3     1007.81 GiB (58%)  |   L  /dev/sdh2 1.07 TiB            
                         |   L  series    1.0 TiB   (58%)   |    /srv/series                                            |  /dev/sdi ATA WDC WD20EARX-00P     
                         |                                  |  dev                          devtmpfs 15.68 GiB   (0%)   |   R  /dev/sdi1 700.0 GiB           
                         |                                  |    /dev                                                   |   L  /dev/sdi2 1.14 TiB            
                         |                                  |  run                          tmpfs    15.69 GiB   (0%)   |                                    
                         |                                  |    /run                                                   |                                    
                         |                                  |  tmpfs                        tmpfs    3.14 GiB    (0%)   |                                    
                         |                                  |    /run/user/1000                                         |
```
