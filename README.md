# Running

```
ansible-galaxy install -r requirements.yml
ansible-galaxy collection install community.general
ansible-playbook --ask-vault-pass -b -e @vm_vars.yml -e @vars/secure.yml -i vm_inventory -k -K playbook.yml
```

# Photo Preparation

Copy all photos to a directory named Unsorted and run the following:
```
exiftool -ee -d "sorted/%Y/%Y%m%d-%H%M%S.%%e" "-filename<CreateDate" .
```

Photos stored from iOS usually have the CreateDate metadata set but, randomly, some do not.
Strangely though, the photos are marked with a date in iCloud.com.
`exiftool` can be used to fix this manually. For example, this sets the create date for
a single image:
```
exiftool -createdate="2019:07:10 12:01:55" IMG_3369.JPG
```

# Backblaze + Restic Preparation

Any new Restic repository must be initialised first before use:
```
sudo su -s /bin/bash backup
. ~/.env
# the name of the Backblaze bucket must be unique
restic -r b2:whizz-onedrive:/ init
```

# Wishlist (in order of preference)

* 2FA Authorisation server
* Email server (https://workaround.org/ispmail/buster/ for setup, https://mail-tester.com for testing, http://www.anti-abuse.org/multi-rbl-check/ for IP blacklist check, relay emails through GMail/PepiPost/Smtp2GO/etc.)
* Wireguard VPN
* Turtl or equivalent bookmarking service with iOS app
* Ebook reader service (e.g. Calibre Web)
* Bitwarden password manager
* Monitoring: metrics aggregator and email alerts
* Rearrange all hard drives to use ZFS/BTRFS/GlusterFS for one large, redundant pool
* File sharing (Nextcloud, Owncloud, Syncthing, etc.)
* Monitoring: logging aggregator
* Home Assistant
* Read it later service (e.g. Wallabag)
* Youtube downloader service (e.g. Alltube)
* Document scanning service (https://github.com/the-paperless-project/paperless)
* RSS reader
* Web games e.g. Chess :)
* Version control service (e.g. Gitlab)

See https://github.com/awesome-selfhosted/awesome-selfhosted for inspiration

# PinePhone Daily Driver

The following apps and functionality must function to use the PinePhone daily:

* Web Browsing
* Hangouts, Whatsapp, Skype messaging
* Gmail, Hotmail, Yahoo Mail and Protonmail receiving
* Photo taking (front + back cameras)
* Automatic photo backups
* Contacts listing
* Contacts backups
* Alarms and timers
* Podcasts
* Music
* Weather
* Calendar + backups
* Bitwarden
* AIB Mobile
* Authy