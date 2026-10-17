# ChupathingyCE Dedicated Server: Pterodactyl egg

Import `egg-chupathingyce-server.json` (Admin > Nests > Import Egg). After you
edit `src/install.sh`, `src/start.sh` or the variables in `build_egg.py`, run
`python3 build_egg.py` to rebuild it.

## How it works

- **Install** (`ghcr.io/pterodactyl/installers:alpine`): downloads the release
  zip for the node's architecture from GitHub, checks it against the release's
  `SHA256SUMS`, and writes out the binary, the stock playlists,
  `blocked_names.txt`, the empty `maps*/` folders and `start.sh`. To update,
  reinstall. Your maps, saves, bans, accounts and `admin/` are left alone.
- **Run** (`ghcr.io/pterodactyl/yolks:alpine`): the binary is static, so any
  image will do. The yolk runs `exec env ash ./start.sh`, and `start.sh` runs
  `exec ./chupathingyce-server`, so the server becomes PID 1 and gets the
  panel's stop signal (`^C` = SIGINT) itself. That way it takes its game off
  the lists when it stops.
- **Network**: internet play is pinned to the primary allocation
  (`HALO_NET_TUNNEL_PORT=$SERVER_PORT`, UDP), and Docker publishes that port.
  That is the README's "fixed, forwarded port" setup, which works behind
  Docker's NAT, though upstream recommends `--network host`. UPnP is turned
  off. System link (5150/5160) only works on a LAN and isn't used.
- **Control panel** (optional): add a second allocation and put its port in
  *Control panel port*. It serves HTTPS with a self-signed certificate. The
  first start prints the token, the certificate fingerprint and the one-time
  owner setup link **on the console**, so anyone with console access to this
  server can see them.
- Blank tunables (max players, welcome, and so on) are taken out of the
  environment, so values saved with `sv_set` or the control panel
  (`admin/settings.toml`) still apply. Anything you fill in on the panel
  overrides them.

## Maps (you supply them)

Upload over SFTP:

- `maps/`: `ui.map` and **all** the multiplayer maps from the NTSC Xbox disc
  (about 300 MB)
- `maps_ce/`: Custom Edition maps, plus CE's `bitmaps.map`, `sounds.map` and
  `loc.map`
- `maps_md/`: HaloMD maps
- `maps_pc/`: Halo PC retail maps

Or set *Maps archive URL* to a private zip or tar.gz of your own copy.

## Resources

At idle it uses about 215 MB of RAM (x64/arm64) or 85 MB (x86), and about 2%
of a core. Give it a 1 GB memory limit and around 1 GB of disk for the maps.

## Things to check on first deploy

1. The console shows `Internet play: this machine's public address is …:<port>`
   with your allocation's port.
2. The node's firewall allows UDP on that port.
3. The panel marks the server "running". That happens when the console shows
   `dedicated: the playlist is`. If it never does, change *Startup > done* in
   the egg to a line your console does show, such as
   `Game list: the game is listed`.
