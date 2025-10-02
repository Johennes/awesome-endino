import json
import requests
import time

ENDINO = "d06cca33-9167-4049-b5ce-6a6aeff60a8d"

def get(path, params):
    print(f"GET {path} {params}")
    return requests.get(
        url = f"https://musicbrainz.org/ws/2{path}",
        params = params,
        headers = {
            "User-Agent": "awesome-endino/trunk (n0-0ne+awesomeendino@mailbox.org)",
            "Accept": "application/json"
        })

artist = get(f"/artist/{ENDINO}", params = { "inc": "recording-rels" }).json()

release_groups_by_id = {}
relation_types_by_release_group_id = {}

for relation in artist["relations"]:
    time.sleep(1.1)

    recording = get(f"/recording/{relation["recording"]["id"]}", { "inc": "artists+releases+release-groups" }).json()

    release_group = recording["releases"][0]["release-group"]
    release_group_id = release_group["id"]
    release_groups_by_id[release_group_id] = release_group

    relation_types = relation_types_by_release_group_id.get(release_group_id, {})
    relation_types[relation["type"]] = relation_types.get(relation["type"], 0) + 1
    relation_types_by_release_group_id[release_group_id] = relation_types

    # if len(release_groups_by_id) > 0:
    #     break

print()
print("| Year | Artist | Release | Credit |")
print("| ---- | ------ | ------- | ------ |")

release_groups = sorted(release_groups_by_id.values(), key = lambda rg: rg["first-release-date"])

def format_artists(release_group):
    artists = []
    for credit in release_group["artist-credit"]:
        name = credit["artist"]["name"]
        id = credit["artist"]["id"]
        artists.append(f"[{name}](https://musicbrainz.org/artist/{id})")
    return " / ".join(artists)

def format_relation_types(relation_types_dict):
    types = []
    for type in sorted(relation_types_dict.keys()):
        count = relation_types_dict[type]
        tracks = "tracks" if count > 1 else "track"
        types.append(f"{type} ({count} {tracks})")
    return ", ".join(types)

for release_group in release_groups:
    id = release_group["id"]
    artists = format_artists(release_group)
    title = release_group["title"]
    date = release_group["first-release-date"][:4]
    relation_types = format_relation_types(relation_types_by_release_group_id[id])

    url = f"https://musicbrainz.org/release-group/{id}"

    print(f"| {date} | {artists} | [{title}]({url}) | {relation_types} |")
