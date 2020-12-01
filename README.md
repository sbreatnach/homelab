# Running

```
ansible-galaxy install -r requirements.yml
ansible-galaxy collection install community.general
ansible-playbook --ask-vault-pass -b -e @vm_vars.yml -e @vars/secure.yml -i vm_inventory -k -K playbook.yml
```

# Photo Preparation

Copy all photos to a directory named sorted and run the following:
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

# Wishlist (in order of preference)

* Setup OneDrive photo backup
* Backups for everything and document restore steps
* Regular backups of iCloud photos + videos
* Wireguard VPN
* Local music streamer (e.g. MPD + web UI)
* Turtl or equivalent bookmarking service with iOS app
* Ebook reader service (e.g. Calibre Web)
* Email server (https://workaround.org/ispmail/buster/ for setup, https://mail-tester.com for testing, http://www.anti-abuse.org/multi-rbl-check/ for IP blacklist check, relay emails through GMail/PepiPost/Smtp2GO/etc.)
* Bitwarden password manager
* Monitoring: metrics aggregator and email alerts
* Rearrange all hard drives to use ZFS/BTRFS/GlusterFS for one large, redundant pool
* File sharing (Nextcloud, Owncloud, Syncthing, etc.)
* Monitoring: logging aggregator
* Snapcast server
* Home Assistant
* Read it later service (e.g. Wallabag)
* Youtube downloader service (e.g. Alltube)
* Document scanning service (https://github.com/the-paperless-project/paperless)
* RSS reader
* Web games e.g. Chess :)
* Version control service (e.g. Gitlab)

See https://github.com/awesome-selfhosted/awesome-selfhosted for inspiration