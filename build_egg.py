#!/usr/bin/env python3
"""Assemble egg-chupathingyce-server.json from src/install.sh and src/start.sh."""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
install = (HERE / "src/install.sh").read_text()
start = (HERE / "src/start.sh").read_text().rstrip("\n")
install = install.replace("@@START_SH@@", start)


def var(name, env, default, rules, description, editable=True, viewable=True):
    return {
        "name": name,
        "description": description,
        "env_variable": env,
        "default_value": default,
        "user_viewable": viewable,
        "user_editable": editable,
        "rules": rules,
        "field_type": "text",
    }


BLANK = " Blank: the server's default, or what the control panel / sv_set saved."

variables = [
    var("Server name", "HALO_DEDICATED_NAME", "My Server",
        "required|string|max:15",
        "The name on halo.milenko.org and the Server Browser. 15 characters at most."),
    var("Playlist", "HALO_DEDICATED", "playlists/free_for_all.txt",
        "required|string|max:128|regex:/^[A-Za-z0-9_][A-Za-z0-9_.\\/-]*\\.txt$/",
        "A playlist inside the server folder: playlists/free_for_all.txt, slayer.txt, "
        "team_slayer.txt, small_maps.txt, big_maps.txt, bloodgulch.txt, gearbox.txt, or your own."),
    var("Maximum players", "HALO_DEDICATED_MAXIMUM_PLAYERS", "",
        "nullable|integer|between:1,128", "Players a game takes (server default 12)." + BLANK),
    var("Minimum players", "HALO_DEDICATED_MINIMUM_PLAYERS", "",
        "nullable|integer|between:1,128",
        "Players a game waits for before its countdown (server default 1)." + BLANK),
    var("Idle limit (minutes)", "HALO_DEDICATED_IDLE_LIMIT", "",
        "nullable|integer|between:0,1440",
        "End a game nobody has scored in for this long; 0 never (server default 5)." + BLANK),
    var("Public", "HALO_DEDICATED_PUBLIC", "true", "required|string|in:true,false",
        "true: listed in the in-game Server Browser. false: only the game list and invite links."),
    var("Welcome message", "HALO_DEDICATED_WELCOME", "",
        "nullable|string|max:127|regex:/^[\\x20-\\x7E]*$/",
        "Chat message ChupathingyCE players get as they join (printable ASCII)." + BLANK),
    var("Post-game seconds", "HALO_DEDICATED_POSTGAME_SECONDS", "",
        "nullable|integer|between:0,300",
        "How long the carnage report shows (server default 20)." + BLANK),
    var("Skip lobby", "HALO_DEDICATED_SKIP_LOBBY", "", "nullable|string|in:true,false",
        "true: start the next game at once when enough players stayed." + BLANK),
    var("Name filter", "HALO_DEDICATED_NAME_FILTER", "", "nullable|string|in:true,false",
        "true: warn and kick players with a name in blocked_names.txt." + BLANK),
    var("Chat", "HALO_DEDICATED_CHAT", "", "nullable|integer|in:0,1,2",
        "2 on, 1 team chat only, 0 off." + BLANK),
    var("Startup commands file", "HALO_DEDICATED_COMMANDS", "",
        "nullable|string|max:128|regex:/^[A-Za-z0-9_][A-Za-z0-9_.\\/-]*$/",
        "A file in the server folder with one console command a line, run once the server hosts (e.g. startup.txt)."),
    var("Control panel port", "CONTROL_PORT", "", "nullable|integer|between:1024,65535",
        "Turns on the web control panel / API on this port. It must be one of this server's "
        "allocations (add a second one). HTTPS with the server's own certificate: check the "
        "fingerprint the console prints. Blank: off.", editable=False),
    var("Control panel TLS", "HALO_DEDICATED_CONTROL_TLS", "auto", "required|string|in:auto,on",
        "auto/on: HTTPS (required on a public address).", editable=False),
    var("List on halo.milenko.org", "HALO_NET_LIST_GAMES", "true", "required|string|in:true,false",
        "false: not on the game list (invites and the Server Browser still work)."),
    var("Delta Stats", "HALO_NET_REPORT_EVENTS", "true", "required|string|in:true,false",
        "Send each game's events (kills, positions, medals...) to halo.milenko.org for match pages "
        "and leaderboards. Player names only, never addresses."),
    var("Events token", "HALO_EVENTS_TOKEN", "", "nullable|string|max:256",
        "A token from the game list's operator: games count as a trusted server's.",
        editable=False, viewable=False),
    var("Server build", "SERVER_ARCH", "auto", "required|string|in:auto,x64,arm64,x86",
        "auto: the node's architecture. x86 (32-bit) runs on x64 nodes too and uses less memory, "
        "but is meant for Xbox maps; use x64/arm64 for Custom Edition and HaloMD maps. Reinstall to apply.",
        editable=False),
    var("Version", "VERSION", "latest", "required|string|max:32|regex:/^[A-Za-z0-9][A-Za-z0-9.-]*$/",
        "A release tag (v0.7.5d) or latest. Reinstall to update.", editable=False),
    var("Maps archive URL", "MAPS_URL", "", "nullable|url|max:512",
        "Optional: a zip or tar.gz of YOUR OWN copy of the maps (maps/ui.map etc. at its top), "
        "fetched at install while maps/ui.map is missing. Otherwise upload over SFTP.",
        editable=False, viewable=False),
]

egg = {
    "_comment": "DO NOT EDIT: FILE GENERATED AUTOMATICALLY BY PTERODACTYL PANEL - PTERODACTYL.IO",
    "meta": {"version": "PTDL_v2", "update_url": "https://raw.githubusercontent.com/JizzyRivers/chupathingyce-pterodactyl-egg/main/egg-chupathingyce-server.json"},
    "exported_at": "2026-10-17T00:00:00+00:00",
    "name": "ChupathingyCE Dedicated Server",
    "author": "29721813+JizzyRivers@users.noreply.github.com",
    "description": (
        "Halo: Combat Evolved dedicated server from ChupathingyCE. Hosts games around the clock "
        "from a playlist, listed on halo.milenko.org and in the ChupathingyCE/OpenCE Server Browser. "
        "Internet play uses the primary allocation (UDP). You supply the game's maps."
    ),
    "features": None,
    "docker_images": {"Alpine": "ghcr.io/pterodactyl/yolks:alpine"},
    "file_denylist": [],
    "startup": "ash ./start.sh",
    "config": {
        "files": "{}",
        "startup": json.dumps({"done": "dedicated: the playlist is"}),
        "logs": "{}",
        "stop": "^C",
    },
    "scripts": {
        "installation": {
            "script": install.replace("\r\n", "\n"),
            "container": "ghcr.io/pterodactyl/installers:alpine",
            "entrypoint": "ash",
        }
    },
    "variables": variables,
}

out = HERE / "egg-chupathingyce-server.json"
out.write_text(json.dumps(egg, indent=4) + "\n")
print(f"wrote {out}")
