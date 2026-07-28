# Plex History to Tautulli
A Python script to convert Plex history from the API to the Tautulli database import format. Born out of spite of all the reddit posts and the FAQ saying it can't be done. 

## Per the FAQ
> _**Q: Can Tautulli import history from before it was installed?**_
>
> _**A:** No, unless you had PlexWatch or Plexivity installed previously and import the database, Tautulli can only start logging history after it is installed._
>
> _Although Plex does keep some information in their database, it is nowhere near detailed enough to build the level of history that Tautulli keeps, the above tools keep enough information to build partial records from._

While it's true that Plex doesn't store as much detailed information as Tautulli can use, it gives enough to give you a _**general**_ idea of what was going on before you had Tautulli installed. 

### Missing Information
As long as you don't care about the following information, then you should be all set to use this:
- IP Addresses
- Product used to watch
- Pauses
- Specific stream information
	- Whether it was LAN, WAN, etc
	- Whether it was direct, copy, or transcode
	- The video and audio specific bit rates, transcode selections
- If the stream was through SSH or not

### Accessible and Accurate Information
What it will give you is:
- Date
- User
- Platform
- Player
- Basic media metadata
	- Title
	- Parent Title
	- Grandparent Title
- Start Time

### Accessible and Inaccurate Information
This script makes the assumption that media was started and watched all the way through with no pauses. This means that even if a user only watched 1 minute of a movie, it would set the stopped and duration to the full movie length.

## Setup
Requirements:
- Python3.12 / Python3.14

Install requirements with `python -m pip install -r requirements.txt`

#### Plex API Key - https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/ 
#### Tautulli API Key - Go into Tautulli Settings > Web Interface > Show Advanced > API Key is at the bottom

### Environment Variables
```env
PLEX_API_KEY=PLEX_ACCESS_TOKEN
PLEX_URL=192.168.1.1
PLEX_PORT=32400
TAUTULLI_URL=192.168.1.1
TAUTULLI_PORT=8181
TAUTULLI_API_KEY=TAUTULLI_API_KEY
```
#### If you don't wish to add ENV variables, you can edit the config.ini files and add the values there instead. 



## Running
The script can be ran with `plex_history_to_tautulli.py`. This will fetch User, Device, Library, Media, and History data from Plex, and User data from Tautulli. This information is used to build as much data as possible for the Tautulli database import.

Once the script is complete, there will be a `plex_to_tautulli.db` file in the folder. This can then be used to upload via the Tautulli Import & Backups menu.

### Options

#### `--mode {both,video,music}`
Selects which history to import. Defaults to `both`.

| Mode | Libraries fetched | History entries read |
| --- | --- | --- |
| `both` | `movie`, `show`, `artist` | `<Video>` and `<Track>` |
| `video` | `movie`, `show` | `<Video>` only |
| `music` | `artist` | `<Track>` only |

```sh
python plex_history_to_tautulli.py --mode music
```

This is useful if you have already imported one type and don't want to duplicate it. Tautulli's import merges rows rather than replacing them, so re-importing history you already have will double the play counts and watch time for that media.

Restricting the mode also skips fetching the libraries you don't need, which saves a significant amount of time. Music libraries in particular require one request per artist plus one request per album, so a large collection can take a while.

#### `--output FILENAME`
Sets the output database filename. By default the file is named after the mode:

| Mode | Default filename |
| --- | --- |
| `both` | `plex_to_tautulli.db` |
| `video` | `plex_to_tautulli_video.db` |
| `music` | `plex_to_tautulli_music.db` |

Separate filenames per mode mean a `--mode music` run will not overwrite the results of an earlier `--mode video` run.

**Note:** the output file is deleted and rebuilt at the start of every run. Don't point `--output` at a file you want to keep.

![tautulliImport](docs/tautulliImport.png)

# Known Issues/Lack of Features

## Library Support
This currently supports `movie`, `show`, and `artist` (music) library types. Other types, such as `photo`, are not supported.

Music tracks are imported with a `full_title` of `Artist - Track`, matching Tautulli's own formatting, and a `media_type` of `track`.

## Missing Media
Media that has been deleted from the Plex server or is just missing metadata will not be included. These entries are usually missing the `ratingKey` from the Plex History API call. These can be verified by going to `http://PLEX_URL:PLEX_PORT/status/sessions/history/all?X-Plex-Token=PLEX_API_KEY&limit=100000`

This affects an entire library at once if that library has been deleted and rebuilt. Plex keeps the play events but drops the `ratingKey` from all of them, so history from the old library is not recoverable even though the same files are still on disk under a new section. It's worth checking the counts per `librarySectionID` in the URL above before a long run, so you know what to expect.

Entries whose `ratingKey` is present but no longer resolves to anything in a fetched library are also skipped, as are entries with an unknown device or an unknown Plex account. Each of these prints a message naming the entry.

## SSH Support
This script appends `http://` to the environment variable `PLEX_URL` and thus only supports `HTTP` at the moment
