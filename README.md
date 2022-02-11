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

# VPN Client Configuration

```shell
# generate Wireguard private and public keys
(umask 077 && wg genkey > wg-private-client.key)
wg pubkey < wg-private-client.key > wg-public-client.key
# create client config file
export PUBLIC_SERVER_KEY=
export PRIVATE_CLIENT_KEY=$(cat wg-private-client.key)
export PUBLIC_CLIENT_KEY=$(cat wg-public-client.key)
export NEW_CLIENT_IP=10.99.0.2
cat > wg-client.conf << EOF
# define the local WireGuard interface (client)
[Interface]

# contents of wg-private-client.key
PrivateKey = ${PRIVATE_CLIENT_KEY}

# the IP address of this client on the WireGuard network
Address=${NEW_CLIENT_IP}/32

# define the remote WireGuard interface (server)
[Peer]

# from "sudo wg show wg0"
PublicKey = ${PUBLIC_SERVER_KEY}

# the IP address of the server on the WireGuard network 
AllowedIPs = 10.99.0.1/32

# public IP address and port of the WireGuard server
Endpoint = vpn.somethinginterestinghere.com:51820
EOF
# update server config to include new peer
sudo tee -a /etc/wireguard/wg0.conf > /dev/null << EOF

[Peer]
PublicKey = ${PUBLIC_CLIENT_KEY}
AllowedIPs = ${NEW_CLIENT_IP}/32
EOF
# image that can be scanned by mobile app for configuration of client
qrencode -r wg-client.conf -l M -o /mnt/Backup/tmp/qrdata.png
```

# Wishlist (in order of preference)

* 2FA Authorisation server
* Wireguard VPN
* Searx search
* Turtl or equivalent bookmarking service with iOS app
* Bitwarden password manager
* Monitoring: metrics aggregator and email alerts
* Rearrange all hard drives to use ZFS/BTRFS/GlusterFS for one large, redundant pool
* Monitoring: logging aggregator
* Youtube downloader service (e.g. Alltube)
* Document scanning service (https://github.com/the-paperless-project/paperless)
* Web games e.g. Chess :)
* Version control service (e.g. Gitlab)
* Backup restore playbook with test process (chore!)

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
* Authy

# Development Environment

* pyenv
* leiningen

License
-------

Because of some code reuse, this repository is licenced under
[GNU General Public License v3.0 or later](https://spdx.org/licenses/GPL-3.0-or-later.html)