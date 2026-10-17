#!/bin/ash
# ChupathingyCE Dedicated Server installer (runs in ghcr.io/pterodactyl/installers:alpine)
set -eu

apk add --no-cache curl unzip jq ca-certificates >/dev/null

REPO=ChupathingyCE/chupathingyce
cd /mnt/server

# Which server: the node's architecture unless the variable says otherwise.
ARCH="${SERVER_ARCH:-auto}"
if [ "$ARCH" = auto ]; then
	case "$(uname -m)" in
		x86_64) ARCH=x64 ;;
		aarch64|arm64) ARCH=arm64 ;;
		i?86) ARCH=x86 ;;
		*) echo "unsupported architecture $(uname -m)"; exit 1 ;;
	esac
fi

if [ -z "${VERSION:-}" ] || [ "$VERSION" = latest ]; then
	TAG=$(curl -fsSL "https://api.github.com/repos/$REPO/releases/latest" | jq -r .tag_name)
else
	TAG="$VERSION"
fi
[ -n "$TAG" ] && [ "$TAG" != null ] || { echo "could not find the release"; exit 1; }

ZIP="chupathingyce-server-linux-$ARCH.zip"
BASE="https://github.com/$REPO/releases/download/$TAG"
echo "Installing $ZIP from $TAG"

# Downloads go in the server folder: the install container's /tmp is a small
# tmpfs (Wings' tmpfs_size, 100 MB by default), too small for a maps archive.
TMP=/mnt/server/.egg-tmp
rm -rf "$TMP" && mkdir -p "$TMP"
trap 'rm -rf "$TMP"' EXIT
curl -fsSL -o "$TMP/$ZIP" "$BASE/$ZIP"
curl -fsSL -o "$TMP/SHA256SUMS" "$BASE/SHA256SUMS"
(cd "$TMP" && grep "  $ZIP\$" SHA256SUMS | sha256sum -c -)
unzip -o -q "$TMP/$ZIP" -d "$TMP/x"

install -m 755 "$TMP/x/chupathingyce-server" ./chupathingyce-server
cat > start.sh <<'EOF'
@@START_SH@@
EOF
chmod 755 start.sh
mkdir -p maps maps_ce maps_md maps_pc playlists saves cache logs licenses
# The release's playlists and name list are refreshed on every reinstall;
# keep your own playlists under other names (or make them in the control
# panel, which saves them in admin/).
cp -f "$TMP"/x/playlists/*.txt playlists/
cp -f "$TMP/x/blocked_names.txt" ./blocked_names.txt
cp -f "$TMP/x/README.md" ./SERVER_README.md
cp -f "$TMP"/x/*LICENSE* "$TMP"/x/*COPYING* "$TMP"/x/*OFL* "$TMP"/x/*CC0* licenses/ 2>/dev/null || true

# Optional: your own archive of the game's maps (zip or tar.gz, holding maps/
# and any of maps_ce/, maps_md/, maps_pc/ at its top). Fetched only while
# maps/ui.map is missing, so a reinstall doesn't download it again.
if [ -n "${MAPS_URL:-}" ] && [ ! -f maps/ui.map ]; then
	echo "Fetching maps from MAPS_URL"
	if curl -fsSL -o "$TMP/maps.archive" "$MAPS_URL"; then
		if unzip -tq "$TMP/maps.archive" >/dev/null 2>&1; then
			unzip -o -q "$TMP/maps.archive" -d /mnt/server || echo "warning: could not unpack the maps archive"
		else
			tar -xzf "$TMP/maps.archive" -C /mnt/server || echo "warning: could not unpack the maps archive"
		fi
		rm -f "$TMP/maps.archive"
	else
		echo "warning: could not download MAPS_URL; upload the maps over SFTP instead"
	fi
	[ -f maps/ui.map ] || echo "warning: still no maps/ui.map"
fi

echo "$TAG ($ARCH)" > .egg-version
echo "Installed ChupathingyCE server $TAG ($ARCH)."
[ -f maps/ui.map ] || echo "Next: upload ui.map and the multiplayer maps to maps/ over SFTP."
