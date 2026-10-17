#!/bin/ash
# ChupathingyCE Dedicated Server launcher for Pterodactyl.
# The egg's installer writes this file; reinstalling the server rewrites it.
cd /home/container || exit 1

# The data folder is the server's home; saves, cache and logs inside it so
# they're in backups and visible over SFTP.
export HALO_DATA_ROOT=/home/container
export HALO_SAVE_ROOT=/home/container/saves
export HALO_CACHE_ROOT=/home/container/cache
export XDG_RUNTIME_DIR=/tmp

# Internet play on the server's primary allocation (UDP). Docker publishes it,
# so the server is reachable the same way as a port-forwarded home server.
export HALO_NET_TUNNEL_PORT="${SERVER_PORT}"
export HALO_NET_ALLOW_UPNP=false

# Pterodactyl's console feeds stdin; read it even if it isn't a terminal.
export HALO_DEDICATED_CONSOLE=true

# The control panel, on a second allocation, when one is given.
if [ -n "${CONTROL_PORT:-}" ]; then
	export HALO_DEDICATED_CONTROL="0.0.0.0:${CONTROL_PORT}"
fi

# Blank panel variables mean "the server's default, or what sv_set / the
# control panel saved in admin/settings.toml": drop them from the environment
# so they don't override that file.
for v in $(env | sed -n 's/^\(HALO_[A-Z0-9_]*\)=$/\1/p'); do
	unset "$v"
done

if [ ! -f maps/ui.map ]; then
	echo "[egg] maps/ui.map is missing: upload ui.map and the multiplayer maps"
	echo "[egg] to the maps/ folder over SFTP (see the egg's notes), then start again."
	exit 1
fi

exec ./chupathingyce-server
