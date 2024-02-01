# Running

```
sudo apt install sshpass
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

# use DNS on VPN server while active
DNS = 10.99.0.1, 1.1.1.1
# Enable the following on Linux w/ systemd-resolved only -
# enables use of DNS with whatever is managing it
#PostUp = resolvectl dns %i 10.99.0.1; resolvectl domain %i "~."
#PreDown = resolvectl revert %i

# define the remote WireGuard interface (server)
[Peer]

# from "sudo wg show wg0"
PublicKey = ${PUBLIC_SERVER_KEY}

# range of IPs allowed to access this VPN node
# if explicitly setting the IP address of the wireguard server,
# this results in a split VPN
AllowedIPs = 10.99.0.1/24
# iOS does not work with the split VPN config, only with full
# tunneling. Thus, we set the allowed IPs to all
# TODO: fix the full tunnel to route internet traffic correctly
#AllowedIPs = 0.0.0.0/0

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
# restart wireguard on server to pick up configuration
sudo systemctl restart wg-quick@wg0.service
```

# Bugs TODO

* Samba starts too early on boot and cannot bind to network interfaces. It works
  on local loop interface and thus does not fail.
* sambauser does not have write access to mounts - add named groups for directories
  and include sambauser into groups
  groupadd music
  usermod -a -G music sambauser
  chgrp -R music /mnt/Backup1/data/Music
  chmod -R g+w /mnt/Backup1/data/Music

# Autofs TODO

Automate autofs install and config. Manual steps taken:

```shell
apt install autofs
tee /etc/auto.master.d/media-drives.autofs << EOF
/mnt/   /etc/auto.ext-usb --timeout=10,defaults
EOF
tee /etc/auto.master.d/media-drives.autofs << EOF
Backup1            -fstype=auto           :/dev/disk/by-uuid/55490f6f-0af7-454c-8b54-878ab03b9ab5
Backup2            -fstype=auto           :/dev/disk/by-uuid/AA6E40366E3FFA21
Backup3            -fstype=auto           :/dev/disk/by-uuid/1FF839686B22CA72
Backup4            -fstype=auto           :/dev/disk/by-uuid/2E29C6372E4CB835
Backup5            -fstype=auto           :/dev/disk/by-uuid/f7e92564-08ce-49a1-aed3-691a6b580db8
EOF
```

# DAAP Support TODO

Manual steps taken:

```shell
sudo apt-get install \
  build-essential git autotools-dev autoconf automake libtool gettext gawk \
  gperf bison flex libconfuse-dev libunistring-dev libsqlite3-dev \
  libavcodec-dev libavformat-dev libavfilter-dev libswscale-dev libavutil-dev \
  libasound2-dev libmxml-dev libgcrypt20-dev libavahi-client-dev zlib1g-dev \
  libevent-dev libplist-dev libsodium-dev libjson-c-dev libwebsockets-dev \
  libcurl4-openssl-dev libprotobuf-c-dev avahi-daemon
mkdir ~/lib/c
cd ~/lib/c
git clone https://github.com/owntone/owntone-server.git
cd owntone-server
git checkout 28.5
autoreconf -i
./configure --prefix=/usr --sysconfdir=/etc --localstatedir=/var --enable-install-user
make
sudo make install
tee /etc/owntone.conf << EOF
# A quick guide to configuring OwnTone:
#
# For regular use, the most important setting to configure is "directories",
# which should be the location of your media. Whatever user you have set as
# "uid" must have read access to this location. If the location is a network
# mount, please see the README.
#
# In all likelihood, that's all you need to do!

general {
	# Username
	# Make sure the user has read access to the library directories you set
	# below, and full access to the databases, log and local audio
	uid = "owntone"

	# Database location
#	db_path = "/var/cache/owntone/songs3.db"

	# Database backup location
	# Uncomment and specify a full path to enable abilty to use REST endpoint
	# to initiate backup of songs3.db
#	db_backup_path = "/var/cache/owntone/songs3.bak"

	# Log file and level
	# Available levels: fatal, log, warning, info, debug, spam
	logfile = "/var/log/owntone.log"
	loglevel = log

	# Admin password for the web interface
	# Note that access to the web interface from computers in
	# "trusted_network" (see below) does not require password
#	admin_password = ""

	# Websocket port for the web interface.
#	websocket_port = 3688

	# Websocket interface to bind listener to (e.g. "eth0"). Default is
	# disabled, which means listen on all interfaces.
#	websocket_interface = ""

	# Sets who is allowed to connect without authorisation. This applies to
	# client types like Remotes, DAAP clients (iTunes) and to the web
	# interface. Options are "any", "localhost" or the prefix to one or
	# more ipv4/6 networks. The default is { "localhost", "192.168", "fd" }
#	trusted_networks = { "localhost", "192.168", "fd" }

	# Enable/disable IPv6
	ipv6 = yes

	# Set this if you want the server to bind to a specific IP address. Can
	# be ipv6 or ipv4. Default (commented out or "::") is to listen on all
	# IP addresses.
#	bind_address = "::"

	# Location of cache database
#	cache_path = "/var/cache/owntone/cache.db"

	# DAAP requests that take longer than this threshold (in msec) get their
	# replies cached for next time. Set to 0 to disable caching.
#	cache_daap_threshold = 1000

	# When starting playback, autoselect speaker (if none of the previously
	# selected speakers/outputs are available)
#	speaker_autoselect = no

	# Most modern systems have a high-resolution clock, but if you are on an
	# unusual platform and experience audio drop-outs, you can try changing
	# this option
#	high_resolution_clock = yes
}

# Library configuration
library {
	# Name of the library as displayed by the clients (%h: hostname). If you
	# change the name after pairing with Remote you may have to re-pair.
	name = "My Music on %h"

	# TCP port to listen on. Default port is 3689 (daap)
	port = 3689

	# Password for the library. Optional.
#	password = ""

	# Directories to index
	directories = { "/mnt/Backup1/data/Music" }

	# Follow symlinks. Default: true.
#	follow_symlinks = true

	# Directories containing podcasts
	# For each directory that is indexed the path is matched against these
	# names. If there is a match all items in the directory are marked as
	# podcasts. Eg. if you index /srv/music, and your podcasts are in
	# /srv/music/Podcasts, you can set this to "/Podcasts".
	# (changing this setting only takes effect after rescan, see the README)
	podcasts = { "/mnt/Backup1/data/Podcasts" }

	# Directories containing audiobooks
	# For each directory that is indexed the path is matched against these
	# names. If there is a match all items in the directory are marked as
	# audiobooks.
	# (changing this setting only takes effect after rescan, see the README)
	audiobooks = { "/mnt/Backup1/data/Audiobooks" }

	# Directories containing compilations (eg soundtracks)
	# For each directory that is indexed the path is matched against these
	# names. If there is a match all items in the directory are marked as
	# compilations.
	# (changing this setting only takes effect after rescan, see the README)
	compilations = { "/Compilations" }

	# Compilations usually have many artists, and sometimes no album artist.
	# If you don't want every artist to be listed in artist views, you can
	# set a single name which will be used for all compilation tracks
	# without an album artist, and for all tracks in the compilation
	# directories.
	# (changing this setting only takes effect after rescan, see the README)
	compilation_artist = "Various Artists"

	# If your album and artist lists are cluttered, you can choose to hide
	# albums and artists with only one track. The tracks will still be
	# visible in other lists, e.g. songs and playlists. This setting
	# currently only works in some remotes.
#	hide_singles = false

	# Internet streams in your playlists will by default be shown in the
	# "Radio" library, like iTunes does. However, some clients (like
	# TunesRemote+) won't show the "Radio" library. If you would also like
	# to have them shown like normal playlists, you can enable this option.
#	radio_playlists = false

	# These are the default playlists. If you want them to have other names,
	# you can set it here.
#	name_library    = "Library"
#	name_music      = "Music"
#	name_movies     = "Movies"
#	name_tvshows    = "TV Shows"
#	name_podcasts   = "Podcasts"
#	name_audiobooks = "Audiobooks"
#	name_radio      = "Radio"

	# Artwork file names (without file type extension)
	# OwnTone will look for jpg and png files with these base names
#	artwork_basenames = { "artwork", "cover", "Folder" }

	# Enable searching for artwork corresponding to each individual media
	# file instead of only looking for album artwork. This is disabled by
	# default to reduce cache size.
#	artwork_individual = false

	# File types the scanner should ignore
	# Non-audio files will never be added to the database, but here you
	# can prevent the scanner from even probing them. This might improve
	# scan time. By default .db, .ini, .db-journal, .pdf and .metadata are
	# ignored.
#	filetypes_ignore = { ".db", ".ini", ".db-journal", ".pdf", ".metadata" }

	# File paths the scanner should ignore
	# If you want to exclude files on a more advanced basis you can enter
	# one or more POSIX regular expressions, and any file with a matching
	# path will be ignored.
#	filepath_ignore = { "myregex" }

	# Disable startup file scanning
	# When OwnTone starts it will do an initial file scan of your
	# library (and then watch it for changes). If you are sure your library
	# never changes while OwnTone is not running, you can disable the
	# initial file scan and save some system ressources. Disabling this scan
	# may lead to OwnTone's database coming out of sync with the
	# library. If that happens read the instructions in the README on how
	# to trigger a rescan.
#	filescan_disable = false

	# Should metadata from m3u playlists, e.g. artist and title in EXTINF,
	# override the metadata we get from radio streams?
#	m3u_overrides = false

	# Should iTunes metadata override ours?
#	itunes_overrides = false

	# Should we import the content of iTunes smart playlists?
#	itunes_smartpl = false

	# Decoding options for DAAP clients
	# Since iTunes has native support for mpeg, mp4a, mp4v, alac and wav,
	# such files will be sent as they are. Any other formats will be decoded
	# to raw wav. If OwnTone detects a non-iTunes DAAP client, it is
	# assumed to only support mpeg and wav, other formats will be decoded.
	# Here you can change when to decode. Note that these settings have no
	# effect on AirPlay.
	# Formats: mp4a, mp4v, mpeg, alac, flac, mpc, ogg, wma, wmal, wmav, aif, wav
	# Formats that should never be decoded
#	no_decode = { "format", "format" }
	# Formats that should always be decoded
#	force_decode = { "format", "format" }

	# Watch named pipes in the library for data and autostart playback when
	# there is data to be read. To exclude specific pipes from watching,
	# consider using the above _ignore options.
#	pipe_autostart = true

	# Enable automatic rating updates
	# If enabled, rating is automatically updated after a song has either been
	# played or skipped (only skipping to the next song is taken into account).
	# The calculation is taken from the beets plugin "mpdstats" (see
	# https://beets.readthedocs.io/en/latest/plugins/mpdstats.html).
	# It consist of calculating a stable rating based only on the play- and
	# skipcount and a rolling rating based on the current rating and the action
	# (played or skipped). Both results are combined with a mix-factor of 0.75:
	# new rating = 0.75 * stable rating + 0.25 * rolling rating)
#	rating_updates = false

	# Allows creating, deleting and modifying m3u playlists in the library directories.
	# Only supported by the player web interface and some mpd clients
	# Defaults to being disabled.
#	allow_modifying_stored_playlists = false

	# A directory in one of the library directories that will be used as the default
	# playlist directory. OwnTone creates new playlists in this directory if only
	# a playlist name is provided (requires "allow_modify_stored_playlists" set to true).
#	default_playlist_directory = ""

	# By default OwnTone will - like iTunes - clear the playqueue if
	# playback stops. Setting clear_queue_on_stop_disable to true will keep
	# the playlist like MPD does. Note that some dacp clients do not show
	# the playqueue if playback is stopped.
#	clear_queue_on_stop_disable = false
}

# Local audio output
audio {
	# Name - used in the speaker list in Remote
	nickname = "Computer"

	# Type of the output (alsa, pulseaudio, dummy or disabled)
	type = "disabled"

	# For pulseaudio output, an optional server hostname or IP can be
	# specified (e.g. "localhost"). If not set, connection is made via local
	# socket.
#	server = ""

	# Audio PCM device name for local audio output - ALSA only
#	card = "default"

	# Mixer channel to use for volume control - ALSA only
	# If not set, PCM will be used if available, otherwise Master.
#	mixer = ""

	# Mixer device to use for volume control - ALSA only
	# If not set, the value for "card" will be used.
#	mixer_device = ""

	# Enable or disable audio resampling to keep local audio in sync with
	# e.g. Airplay. This feature relies on accurate ALSA measurements of
	# delay, and some devices don't provide that. If that is the case you
	# are better off disabling the feature.
#	sync_disable = false

	# Here you can adjust when local audio is started relative to other
	# speakers, e.g. Airplay. Negative values correspond to moving local
	# audio ahead, positive correspond to delaying it. The unit is
	# milliseconds. The offset must be between -1000 and 1000 (+/- 1 sec).
#	offset_ms = 0

	# To calculate what and if resampling is required, local audio delay is
	# measured each second. After a period the collected measurements are
	# used to estimate drift and latency, which determines if corrections
	# are required. This setting sets the length of that period in seconds.
#	adjust_period_seconds = 100
}

# ALSA device settings
# If you have multiple ALSA devices you can configure them individually via
# sections like the below. Make sure to set the "card name" correctly. See the
# README about ALSA for details. Note that these settings will override the ALSA
# settings in the "audio" section above.
#alsa "card name" {
	# Name used in the speaker list. If not set, the card name will be used.
#	nickname = "Computer"

	# Mixer channel to use for volume control
	# If not set, PCM will be used if available, otherwise Master
#	mixer = ""

	# Mixer device to use for volume control
	# If not set, the card name will be used
#	mixer_device = ""
#}

# Pipe output
# Allows OwnTone to output audio data to a named pipe
#fifo {
#	nickname = "fifo"
#	path = "/path/to/fifo"
#}

# AirPlay settings common to all devices
#airplay_shared {
        # UDP ports used when airplay devices make connections back to
	# OwnTone (choosing specific ports may be helpful when running
	# OwnTone behind a firewall)
#       control_port = 0
#       timing_port = 0
#}

# AirPlay per device settings
# (make sure you get the capitalization of the device name right)
#airplay "My AirPlay device" {
	# OwnTone's volume goes to 11! If that's more than you can handle
	# you can set a lower value here
#	max_volume = 11

	# Enable this option to exclude a particular AirPlay device from the
	# speaker list
#	exclude = false

	# Enable this option to keep a particular AirPlay device in the speaker
	# list and thus ignore mdns notifications about it no longer being
	# present. The speaker will remain until restart of OwnTone.
#	permanent = false

	# Some devices spuriously disconnect during playback, and based on the
	# device type OwnTone may attempt to reconnect. Setting this option
	# overrides this so reconnecting is either always enabled or disabled.
#	reconnect = false

	# AirPlay password
#	password = "s1kr3t"

	# Disable AirPlay 1 (RAOP)
#	raop_disable = false

	# Name used in the speaker list, overrides name from the device
#	nickname = "My speaker name"
#}

# Chromecast settings
# (make sure you get the capitalization of the device name right)
#chromecast "My Chromecast device" {
	# OwnTone's volume goes to 11! If that's more than you can handle
	# you can set a lower value here
#	max_volume = 11

	# Enable this option to exclude a particular device from the speaker
	# list
#	exclude = false

	# Name used in the speaker list, overrides name from the device
#	nickname = "My speaker name"
#}

# Spotify settings (only have effect if Spotify enabled - see README/INSTALL)
spotify {
	# Set preferred bitrate for music streaming
	# 0: No preference (default), 1: 96kbps, 2: 160kbps, 3: 320kbps
#	bitrate = 0

	# Your Spotify playlists will by default be put in a "Spotify" playlist
	# folder. If you would rather have them together with your other
	# playlists you can set this option to true.
#	base_playlist_disable = false

	# Spotify playlists usually have many artist, and if you don't want
	# every artist to be listed when artist browsing in Remote, you can set
	# the artist_override flag to true. This will use the compilation_artist
	# as album artist for Spotify items.
#	artist_override = false

	# Similar to the different artists in Spotify playlists, the playlist
	# items belong to different albums, and if you do not want every album
	# to be listed when browsing in Remote, you can set the album_override
	# flag to true. This will use the playlist name as album name for
	# Spotify items. Notice that if an item is in more than one playlist,
	# it will only appear in one album when browsing (in which album is
	# random).
#	album_override = false
}

# RCP/Roku Soundbridge output settings
# (make sure you get the capitalization of the device name right)
#rcp "My SoundBridge device" {
	# Enable this option to exclude a particular device from the speaker
	# list
#	exclude = false

	# A Roku/SoundBridge can power up in 2 modes: (default) reconnect to the 
	# previously used library (ie OwnTone) or in a 'cleared library' mode.
	# The Roku power up behaviour is affected by how OwnTone disconnects
	# from the Roku device.
	#
	# Set to false to maintain default Roku power on behaviour
#	clear_on_close = false
#}


# MPD configuration (only have effect if MPD enabled - see README/INSTALL)
mpd {
	# TCP port to listen on for MPD client requests.
	# Default port is 6600, set to 0 to disable MPD support.
	port = 0

	# HTTP port to listen for artwork requests (only supported by some MPD
	# clients and will need additional configuration in the MPD client to
	# work). Set to 0 to disable serving artwork over http.
#	http_port = 0
}

# SQLite configuration (allows to modify the operation of the SQLite databases)
# Make sure to read the SQLite documentation for the corresponding PRAGMA
# statements as changing them from the defaults may increase the possibility of
# database corruptions! By default the SQLite default values are used.
sqlite {
	# Cache size in number of db pages for the library database
	# (SQLite default page size is 1024 bytes and cache size is 2000 pages)
#	pragma_cache_size_library = 2000

	# Cache size in number of db pages for the daap cache database
	# (SQLite default page size is 1024 bytes and cache size is 2000 pages)
#	pragma_cache_size_cache = 2000

	# Sets the journal mode for the database
	# DELETE (default), TRUNCATE, PERSIST, MEMORY, WAL, OFF
#	pragma_journal_mode = DELETE

	# Change the setting of the "synchronous" flag
	# 0: OFF, 1: NORMAL, 2: FULL (default)
#	pragma_synchronous = 2

	# Number of bytes set aside for memory-mapped I/O  for the library database
	# (requires sqlite 3.7.17 or later)
	# 0: disables mmap (default), any other value > 0: number of bytes for mmap
#	pragma_mmap_size_library = 0

	# Number of bytes set aside for memory-mapped I/O for the cache database
	# (requires sqlite 3.7.17 or later)
	# 0: disables mmap (default), any other value > 0: number of bytes for mmap
#	pragma_mmap_size_cache = 0

	# Should the database be vacuumed on startup? (increases startup time,
	# but may reduce database size). Default is yes.
#	vacuum = yes
}

# Streaming audio settings for remote connections (ie stream.mp3)
streaming {
	# Sample rate, typically 44100 or 48000
#	sample_rate = 44100

	# Set the MP3 streaming bit rate (in kbps), valid options: 64 / 96 / 128 / 192 / 320
#	bit_rate = 192
}
EOF
```

Avahi-daemon has [a long-standing bug](https://github.com/lathiat/avahi/issues/117)
with randomly changing reported mDNS entries.
Attempted fix to config:
```shell
tee /etc/avahi/avahi-daemon.conf << EOF
[server]
#host-name=foo
#domain-name=local
#browse-domains=0pointer.de, zeroconf.org
use-ipv4=yes
use-ipv6=yes
# CUSTOM: setting explicit interface, skipping local loop
allow-interfaces=eno1
#deny-interfaces=eth1
#check-response-ttl=no
#use-iff-running=no
#enable-dbus=yes
#disallow-other-stacks=no
#allow-point-to-point=no
#cache-entries-max=4096
#clients-max=4096
#objects-per-client-max=1024
#entries-per-entry-group-max=32
ratelimit-interval-usec=1000000
ratelimit-burst=1000

[wide-area]
enable-wide-area=yes

[publish]
#disable-publishing=no
#disable-user-service-publishing=no
#add-service-cookie=no
#publish-addresses=yes
publish-hinfo=no
publish-workstation=no
#publish-domain=yes
#publish-dns-servers=192.168.50.1, 192.168.50.2
#publish-resolv-conf-dns-servers=yes
#publish-aaaa-on-ipv4=yes
#publish-a-on-ipv6=no

[reflector]
#enable-reflector=no
#reflect-ipv=no
#reflect-filters=_airplay._tcp.local,_raop._tcp.local

[rlimits]
#rlimit-as=
#rlimit-core=0
#rlimit-data=8388608
#rlimit-fsize=0
#rlimit-nofile=768
#rlimit-stack=8388608
#rlimit-nproc=3
EOF
```

# Wishlist (in order of preference)

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
* Whatsapp, Facebook Messenger, Skype messaging
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
* 2FA app with auto-backup to Nextcloud/OneDrive/etc.

# Development Environment

* pyenv
* leiningen

License
-------

Because of some code reuse, this repository is licenced under
[GNU General Public License v3.0 or later](https://spdx.org/licenses/GPL-3.0-or-later.html)