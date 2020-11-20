
```
ansible-galaxy install -r requirements.yml
ansible-galaxy collection install community.general
ansible-playbook --ask-vault-pass -b -e @vm_vars.yml -e @vars/secure.yml -i vm_inventory -k -K playbook.yml
```

# Wishlist

* Wireguard VPN
* Matrix bridges for Facebook Messenger + Whatsapp + Hangouts
* Turtl
* Snapcast server
* Local music streamer (e.g. MPD + web UI)
* Bitwarden password manager
* Logging aggregator
* Metrics aggregator
* Email server
* Ebook reader service (e.g. Calibre Web)
* Youtube downloader service (e.g. Alltube)
* Bookmarking service
* Document scanning service (https://github.com/the-paperless-project/paperless)
* RSS reader
* File sharing (Nextcloud, Owncloud, Syncthing, etc.)
* Chess :)
* Home Assistant
* Read it later service (e.g. Wallabag)
* Version control service (e.g. Gitlab)

See https://github.com/awesome-selfhosted/awesome-selfhosted for inspiration