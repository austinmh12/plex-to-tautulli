from __future__ import annotations

import requests as r
from bs4 import BeautifulSoup as Soup
from dotenv import load_dotenv
from os import environ, remove
from sqlite3 import connect
import configparser as conf

load_dotenv()

try:
    PLEX_URL = f'http://{environ["PLEX_URL"]}:{environ["PLEX_PORT"]}'
    PLEX_TOKEN = f'X-Plex-Token={environ["PLEX_API_KEY"]}'
    TAUTULLI_URL = f'http://{environ["TAUTULLI_URL"]}:{environ["TAUTULLI_PORT"]}/api/v2?apikey={environ["TAUTULLI_API_KEY"]}'
except KeyError:
    config = conf.ConfigParser()
    config.read('config.ini')
    PLEX_URL = f'http://{config["DEFAULT"]["PLEX_URL"]}:{config["DEFAULT"]["PLEX_PORT"]}'
    PLEX_TOKEN = f'X-Plex-Token={config["DEFAULT"]["PLEX_API_KEY"]}'
    TAUTULLI_URL = f'http://{config["DEFAULT"]["TAUTULLI_URL"]}:{config["DEFAULT"]["TAUTULLI_PORT"]}/api/v2?apikey={config["DEFAULT"]["TAUTULLI_API_KEY"]}'


class TautulliUser:
	def __init__(self, user_id: int, username: str, **kwargs) -> None:
		self.user_id: int = user_id
		self.username: str = username

	def __repr__(self) -> str:
		return f'TautulliUser(user_id={self.user_id}, username={self.username})'

class PlexUser:
	def __init__(
		self,
		id: str,
		key: str,
		name: str,
		**kwargs
	) -> None:
		self.id = id
		self.key = key
		self.name = name
	
	def __repr__(self) -> str:
		return f'PlexUser(id={self.id}, name={self.name})'
	
class PlexDevice:
	def __init__(
		self,
		id: str,
		name: str,
		platform: str | None,
		**kwargs
	) -> None:
		self.id = id
		self.name = name
		self.platform = platform

	def __repr__(self) -> str:
		return f'PlexDevice(id={self.id}, name={self.name}, platform={self.platform})'
	
class PlexLibrary:
	def __init__(
		self,
		key: str,
		title: str,
		**kwargs
	) -> None:
		self.key = key
		self.title = title
		self.type_ = kwargs.get('type')

	@property
	def section_id(self) -> str:
		return self.key

	def __repr__(self) -> str:
		return f'PlexLibrary(key={self.key}, title={self.title}, type={self.type_})'
	
class PlexMedia:
	"""Represents either a Movie, or an episode from a TV season from a TV show"""
	def __init__(
		self,
		**kwargs
	) -> None:
		# Universal
		self.key: str = kwargs.get('key', '')
		self.rating_key: str = kwargs.get('ratingKey', '')
		self.type_: str = kwargs.get('type', '')
		self.title: str = kwargs.get('title', '')
		self.thumb: str = kwargs.get('thumb', '')
		self.art: str = kwargs.get('art', '')
		self.duration: str = kwargs.get('duration', '')
		self.year: str = kwargs.get('year', '')
		self.originally_available_at: str = kwargs.get('originallyAvailableAt', '')
		self.added_at: str = kwargs.get('addedAt', '')
		self.updated_at: str = kwargs.get('updatedAt', '')
		self.content_rating: str = kwargs.get('contentRating', '')
		self.summary: str = kwargs.get('summary', '')
		self.rating: str = kwargs.get('rating', '')
		self.guid: str = kwargs.get('guid', '')
		self.directors: list[str] = kwargs.get('directors', '')
		self.writers: list[str] = kwargs.get('writers', '')
		self.actors: list[str] = kwargs.get('actors', '')
		self.genres: list[str] = kwargs.get('genres', '')
		self.studio: str = kwargs.get('studio', '')
		self.bitrate: str = kwargs.get('bitrate', '')
		self.container: str = kwargs.get('container', '')
		self.width: str = kwargs.get('width', '')
		self.height: str = kwargs.get('height', '')
		self.aspect_ratio: str = kwargs.get('aspectRatio', '')
		# self.video_resolution: str = kwargs.get('videoResolution')
		# self.video_frame_rate: str = kwargs.get('videoFrameRate')
		# self.video_codec: str = kwargs.get('videoCodec')

		# Movies only
		self.tagline: str = kwargs.get('tagline', '')

		# Shows only
		self.index: str = kwargs.get('index', '')
		self.last_viewed_at: str = kwargs.get('lastViewedAt', '')
		self.parent_index: str = kwargs.get('parentIndex', '')
		self.parent_title: str = kwargs.get('parentTitle', '')
		self.parent_thumb: str = kwargs.get('parentThumb', '')
		self.parent_rating_key: str = kwargs.get('parentRatingKey', '')
		self.grandparent_index: str = kwargs.get('grandparentIndex', '')
		self.grandparent_title: str = kwargs.get('grandparentTitle', '')
		self.grandparent_thumb: str = kwargs.get('grandparentThumb', '')
		self.grandparent_rating_key: str = kwargs.get('grandparentRatingKey', '')

	def __repr__(self) -> str:
		return f'PlexMedia(key={self.key}, title={self.title})'

class PlexHistory:
	def __init__(
		self,
		**kwargs
	) -> None:
		self.history_key: str | None = kwargs.get('historyKey')
		self.key: str | None = kwargs.get('key')
		self.rating_key: str | None = kwargs.get('ratingKey')
		self.library_section_id: str | None = kwargs.get('librarySectionID')
		self.parent_key: str | None = kwargs.get('parentKey')
		self.grandparent_key: str | None = kwargs.get('grandparentKey')
		self.title: str | None = kwargs.get('title')
		self.grandparent_title: str | None = kwargs.get('grandparentTitle')
		self.type_: str | None = kwargs.get('type')
		self.thumb: str | None = kwargs.get('thumb')
		self.parent_thumb: str | None = kwargs.get('parentThumb')
		self.grandparent_thumb: str | None = kwargs.get('grandparentThumb')
		self.grandparent_art: str | None = kwargs.get('grandparentArt')
		self.index: str | None = kwargs.get('index')
		self.parent_index: str | None = kwargs.get('parentIndex')
		self.originally_available_at: str | None = kwargs.get('originallyAvailableAt')
		self.viewed_at: str | None = kwargs.get('viewedAt')
		self.account_id: str | None = kwargs.get('accountID')
		self.device_id: str | None = kwargs.get('deviceID')

def main():
	""""""
	# Fetch all plex users for easy lookup
	plex_users = {u.id: u for u in fetch_plex_users()}
	# Fetch all the tautulli users to map plex users
	tautulli_users = fetch_tautulli_users()
	tautulli_users_by_username = {t.username: t for t in tautulli_users}
	tautulli_users_by_user_id = {t.user_id: t for t in tautulli_users}
	# Fetch all plex devices for easy lookup
	devices = {d.id: d for d in fetch_plex_devices()}
	# Fetch all libraries
	libraries = {l.key: l for l in fetch_plex_libraries()}
	# Fetch the following based on the libraries
	medias: list[PlexMedia] = []
	for library in libraries.values():
		# Fetch all plex movies
		if library.type_ == 'movie':
			data = fetch_movie_media(library)
			medias.extend(data)
		# Fetch all plex tv shows
		if library.type_ == 'show':
			data = fetch_show_media(library)
			medias.extend(data)
	media_dict: dict[str, PlexMedia] = {m.rating_key: m for m in medias}
	# Fetch all plex session history
	history = fetch_plex_history()
	# For each session history entry
	inserts: list[tuple[PlexHistory, PlexMedia, PlexDevice, TautulliUser]] = []
	for hist in history:
		# Find the matching media
		# TODO: Try and use medias to look this up
		if hist.rating_key is None:
			print(f'No rating key for {hist.history_key}, skipping')
			continue
		media = media_dict.get(hist.rating_key)
		if media is None:
			print(f'No media in library for {hist.title} ({hist.rating_key}), skipping')
			continue
		# Find the matching device
		device = devices.get(hist.device_id)
		if device is None:
			print(f'No device {hist.device_id} for {hist.title}, skipping')
			continue
		# Find the matching user and map to tautulli ID
		user = tautulli_users_by_user_id.get(int(hist.account_id))
		if user is None:
			plex_user = plex_users.get(hist.account_id)
			if plex_user is None:
				print(f'Unable to find plex account {hist.account_id} for {hist.title}, skipping')
				continue
			tautulli_user = tautulli_users_by_username.get(plex_user.name)
			if tautulli_user is None:
				print(f'Unable to find user for {hist.title}, skipping')
				print(hist.__dict__)
				continue
			user = tautulli_user
		inserts.append((hist, media, device, user))

def fetch_plex_users() -> list[PlexUser]:
	"""Fetches all the plex users in the plex server."""
	resp = r.get(f'{PLEX_URL}/accounts?{PLEX_TOKEN}')
	xml = Soup(resp.text, 'xml')
	return [PlexUser(**a.attrs) for a in xml('Account')]

def fetch_tautulli_users() -> list[TautulliUser]:
	"""Fetches all the tautulli users in the server."""
	resp = r.get(f'{TAUTULLI_URL}&cmd=get_users').json().get('response', {}).get('data', [])
	return [TautulliUser(**u) for u in resp]

def fetch_plex_devices() -> list[PlexDevice]:
	"""Fetches all the plex devices in the plex server."""
	resp = r.get(f'{PLEX_URL}/devices?{PLEX_TOKEN}')
	xml = Soup(resp.text, 'xml')
	return [PlexDevice(**d.attrs) for d in xml('Device')]

def fetch_plex_libraries() -> list[PlexLibrary]:
	"""Fetches all the plex libraries in the plex server."""
	resp = r.get(f'{PLEX_URL}/library/sections/?{PLEX_TOKEN}')
	xml = Soup(resp.text, 'xml')
	return [PlexLibrary(**l.attrs) for l in xml('Directory')]

def fetch_movie_media(lib: PlexLibrary) -> list[PlexMedia]:
	"""Fetches all the movies in a plex library."""
	resp = r.get(f'{PLEX_URL}/library/sections/{lib.section_id}/all?{PLEX_TOKEN}&limit=100000&includeGuids=true')
	xml = Soup(resp.text, 'xml')
	medias = []
	for video in xml('Video'):
		media_dict = {}
		media_dict.update(video.attrs)
		media_dict.update(video.Media.attrs)
		media_dict['genres'] = ';'.join([g.attrs['tag'] for g in video('Genre')])
		media_dict['directors'] = ';'.join([g.attrs['tag'] for g in video('Director')])
		media_dict['writers'] = ';'.join([g.attrs['tag'] for g in video('Writer')])
		media_dict['actors'] = ';'.join([g.attrs['tag'] for g in video('Role')])
		media = PlexMedia(**media_dict)
		# print(media)
		medias.append(media)
	return medias

def fetch_show_media(lib: PlexLibrary) -> list[PlexMedia]:
	"""Fetches all the episodes in each season of each TV show."""
	resp = r.get(f'{PLEX_URL}/library/sections/{lib.section_id}/all?{PLEX_TOKEN}&limit=100000&includeGuids=true')
	xml = Soup(resp.text, 'xml')
	medias = []
	for show in xml('Directory'):
		resp = r.get(f'{PLEX_URL}/library/metadata/{show.attrs["ratingKey"]}/children?{PLEX_TOKEN}')
		season_xml = Soup(resp.text, 'xml')
		seasons = [s for s in season_xml('Directory') if 'ratingKey' in s.attrs]
		for season in seasons:
			resp = r.get(f'{PLEX_URL}/library/metadata/{season.attrs["ratingKey"]}/children?{PLEX_TOKEN}')
			episode_xml = Soup(resp.text, 'xml')
			for episode in episode_xml('Video'):
				media_dict = {}
				media_dict.update(episode.attrs)
				media_dict.update(episode.Media.attrs)
				media_dict['genres'] = ';'.join([g.attrs['tag'] for g in show('Genre')])
				media_dict['directors'] = ';'.join([g.attrs['tag'] for g in show('Director')])
				media_dict['writers'] = ';'.join([g.attrs['tag'] for g in show('Writer')])
				media_dict['actors'] = ';'.join([g.attrs['tag'] for g in show('Role')])
				media_dict['lastViewedAt'] = show.attrs.get('lastViewedAt', '')
				media_dict['studio'] = show.attrs.get('studio', '')
				media = PlexMedia(**media_dict)
				# print(media.__dict__)
				medias.append(media)
	return medias

def fetch_plex_history() -> list[PlexHistory]:
	"""Fetches all the history from the plex server."""
	resp = r.get(f'{PLEX_URL}/status/sessions/history/all?{PLEX_TOKEN}&limit=100000')
	xml = Soup(resp.text, 'xml')
	return [PlexHistory(**h.attrs) for h in xml('Video')]

def insert_history(histories: list[tuple[PlexHistory, PlexMedia, PlexDevice, TautulliUser]]):
	"""Inserts the histories into the plex_to_tautulli.db file"""
	db = connect('plex_to_tautulli.db', isolation_level=None, autocommit=True)
	for i, (history, media, device, user) in enumerate(histories, start=1):
		db.execute(
			'''
			insert into session_history_metadata (rating_key, parent_rating_key, grandparent_rating_key, title,
			parent_title, grandparent_title, original_title, full_title, media_index, parent_media_index, thumb,
			parent_thumb, grandparent_thumb, art, media_type, year, originally_available_at, added_at, updated_at,
			last_viewed_at, content_rating, summary, tagline, rating, duration, guid, directors, writers, actors, genres, studio, live,
			channel_call_sign, channel_id, channel_identifier, channel_title, channel_thumb, channel_vcn,
			marker_credits_first, marker_credits_final) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
			?,?,?,?,?,?,?,?,?,?);
			''',
			(
				history.rating_key, 
				media.parent_rating_key,
				media.grandparent_rating_key,
				media.title,
				media.parent_title,
				media.grandparent_title,
				'', # original title
				media.title if media.type_ == 'movie' else f'{media.grandparent_title} - {media.title}',
				media.index,
				media.parent_index,
				media.thumb,
				media.parent_thumb,
				media.grandparent_thumb,
				media.art,
				media.type_,
				media.year,
				media.originally_available_at,
				media.added_at,
				media.updated_at,
				media.last_viewed_at,
				media.content_rating,
				media.summary,
				media.tagline,
				media.rating,
				media.duration,
				media.guid,
				media.directors,
				media.writers,
				media.actors,
				media.genres,
				media.studio,
				0, # Never live for me
				'', '', '', '', '', '', None, None # channel and marker data is going to be null here
			)
		)
		db.execute(
			'''
			insert into session_history_media_info (rating_key, duration, container, bitrate, width, height, 
			aspect_ratio) values (?,?,?,?,?,?,?);
			''',
			(media.rating_key, media.duration, media.container, media.bitrate, media.width, media.height, media.aspect_ratio)
		)
		db.execute(
			'''
			insert into session_history (reference_id, started, stopped, rating_key, user_id, user, paused_counter,
			player, platform, parent_rating_key, grandparent_rating_key, media_type, section_id, view_offset) values 
			(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
			''',
			(
				i,
				history.viewed_at,
				# media duration is in milliseconds, viewed at is epoch time in seconds
				int(history.viewed_at) + (int(media.duration) // 1000),
				media.rating_key,
				user.user_id,
				user.username,
				0,
				device.name,
				device.platform,
				media.parent_rating_key,
				media.grandparent_rating_key,
				media.type_,
				history.library_section_id,
				0
			)
		)
	db.close()

def init_db():
	try:
		remove('plex_to_tautulli.db')
	except OSError:
		pass
	db = connect('plex_to_tautulli.db', isolation_level=None, autocommit=True)
	db.execute('CREATE TABLE if not exists session_history (id INTEGER PRIMARY KEY AUTOINCREMENT, reference_id INTEGER, started INTEGER, stopped INTEGER, rating_key INTEGER, user_id INTEGER, user TEXT, ip_address TEXT, paused_counter INTEGER DEFAULT 0, player TEXT, product TEXT, product_version TEXT, platform TEXT, platform_version TEXT, profile TEXT, machine_id TEXT, bandwidth INTEGER, location TEXT, quality_profile TEXT, secure INTEGER, relayed INTEGER, parent_rating_key INTEGER, grandparent_rating_key INTEGER, media_type TEXT, section_id INTEGER, view_offset INTEGER DEFAULT 0);', ())
	db.execute('CREATE INDEX if not exists idx_session_history_media_type ON session_history (media_type);', ())
	db.execute('CREATE INDEX if not exists idx_session_history_media_type_stopped ON session_history (media_type, stopped ASC);', ())
	db.execute('CREATE INDEX if not exists idx_session_history_rating_key ON session_history (rating_key);', ())
	db.execute('CREATE INDEX if not exists idx_session_history_parent_rating_key ON session_history (parent_rating_key);', ())
	db.execute('CREATE INDEX if not exists idx_session_history_grandparent_rating_key ON session_history (grandparent_rating_key);', ())
	db.execute('CREATE INDEX if not exists idx_session_history_user ON session_history (user);', ())
	db.execute('CREATE INDEX if not exists idx_session_history_user_id ON session_history (user_id);', ())
	db.execute('CREATE INDEX if not exists idx_session_history_user_id_stopped ON session_history (user_id, stopped ASC);', ())
	db.execute('CREATE INDEX if not exists idx_session_history_section_id ON session_history (section_id);', ())
	db.execute('CREATE INDEX if not exists idx_session_history_section_id_stopped ON session_history (section_id, stopped ASC);', ())
	db.execute('CREATE INDEX if not exists idx_session_history_reference_id ON session_history (reference_id ASC);', ())
	db.execute('CREATE TABLE if not exists session_history_metadata (id INTEGER PRIMARY KEY, rating_key INTEGER, parent_rating_key INTEGER, grandparent_rating_key INTEGER, title TEXT, parent_title TEXT, grandparent_title TEXT, original_title TEXT, full_title TEXT, media_index INTEGER, parent_media_index INTEGER, thumb TEXT, parent_thumb TEXT, grandparent_thumb TEXT, art TEXT, media_type TEXT, year INTEGER, originally_available_at TEXT, added_at INTEGER, updated_at INTEGER, last_viewed_at INTEGER, content_rating TEXT, summary TEXT, tagline TEXT, rating TEXT, duration INTEGER DEFAULT 0, guid TEXT, directors TEXT, writers TEXT, actors TEXT, genres TEXT, studio TEXT, labels TEXT, live INTEGER DEFAULT 0, channel_call_sign TEXT, channel_id TEXT, channel_identifier TEXT, channel_title TEXT, channel_thumb TEXT, channel_vcn TEXT, marker_credits_first INTEGER DEFAULT NULL, marker_credits_final INTEGER DEFAULT NULL);', ())
	db.execute('CREATE INDEX if not exists idx_session_history_metadata_rating_key ON session_history_metadata (rating_key);', ())
	db.execute('CREATE INDEX if not exists idx_session_history_metadata_guid ON session_history_metadata (guid);', ())
	db.execute('CREATE INDEX if not exists idx_session_history_metadata_live ON session_history_metadata (live);', ())
	db.execute('CREATE TABLE if not exists session_history_media_info (id INTEGER PRIMARY KEY, rating_key INTEGER, video_decision TEXT, audio_decision TEXT, transcode_decision TEXT, duration INTEGER DEFAULT 0, container TEXT, bitrate INTEGER, width INTEGER, height INTEGER, video_bitrate INTEGER, video_bit_depth INTEGER, video_codec TEXT, video_codec_level TEXT, video_width INTEGER, video_height INTEGER, video_resolution TEXT, video_framerate TEXT, video_scan_type TEXT, video_full_resolution TEXT, video_dynamic_range TEXT, aspect_ratio TEXT, audio_bitrate INTEGER, audio_codec TEXT, audio_channels INTEGER, audio_language TEXT, audio_language_code TEXT, subtitles INTEGER, subtitle_codec TEXT, subtitle_forced, subtitle_language TEXT,transcode_protocol TEXT, transcode_container TEXT, transcode_video_codec TEXT, transcode_audio_codec TEXT, transcode_audio_channels INTEGER, transcode_width INTEGER, transcode_height INTEGER, transcode_hw_requested INTEGER, transcode_hw_full_pipeline INTEGER, transcode_hw_decode TEXT, transcode_hw_decode_title TEXT, transcode_hw_decoding INTEGER, transcode_hw_encode TEXT, transcode_hw_encode_title TEXT, transcode_hw_encoding INTEGER, stream_container TEXT, stream_container_decision TEXT, stream_bitrate INTEGER, stream_video_decision TEXT, stream_video_bitrate INTEGER, stream_video_codec TEXT, stream_video_codec_level TEXT, stream_video_bit_depth INTEGER, stream_video_height INTEGER, stream_video_width INTEGER, stream_video_resolution TEXT, stream_video_framerate TEXT, stream_video_scan_type TEXT, stream_video_full_resolution TEXT, stream_video_dynamic_range TEXT, stream_audio_decision TEXT, stream_audio_codec TEXT, stream_audio_bitrate INTEGER, stream_audio_channels INTEGER, stream_audio_language TEXT, stream_audio_language_code TEXT, stream_subtitle_decision TEXT, stream_subtitle_codec TEXT, stream_subtitle_container TEXT, stream_subtitle_forced INTEGER, stream_subtitle_language TEXT, synced_version INTEGER, synced_version_profile TEXT, optimized_version INTEGER, optimized_version_profile TEXT, optimized_version_title TEXT);', ())
	db.execute('CREATE INDEX if not exists idx_session_history_media_info_transcode_decision ON session_history_media_info (transcode_decision);', ())
	db.execute('CREATE TABLE if not exists version_info (key TEXT UNIQUE, value TEXT);')
	db.execute('insert into version_info (key, value) values (?, ?)', ('version', 'v2.15.2'))
	db.close()

if __name__ == "__main__":
	init_db()
	main()
