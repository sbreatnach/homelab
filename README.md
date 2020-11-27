# Running

```
ansible-galaxy install -r requirements.yml
ansible-galaxy collection install community.general
ansible-playbook --ask-vault-pass -b -e @vm_vars.yml -e @vars/secure.yml -i vm_inventory -k -K playbook.yml
```

# Wishlist (in order of preference)

* Matrix bridges for Facebook Messenger + Whatsapp + Hangouts
* Hosted Matrix web app configured for homeserver e.g. Element
* Backups for everything and document restore steps
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