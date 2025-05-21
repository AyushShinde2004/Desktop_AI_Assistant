import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import re
from thefuzz import fuzz, process
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')

SCOPE = 'user-read-playback-state user-modify-playback-state user-library-read user-read-currently-playing'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
))

# Function to play/Search Spotify
def fuzzy_match_song(song_name, tracks):
    """
    tracks: list of tuples (track_name, artist_name, uri)
    Returns the best matching track uri or None
    """
    from thefuzz import fuzz, process

    full_strings = [f"{track} by {artist}" for track, artist, uri in tracks]
    
    # 1. Try to match full "track by artist"
    best_full = process.extractOne(
        song_name,
        full_strings,
        scorer=fuzz.token_sort_ratio
    )
    if best_full and best_full[1] > 75:
        idx = full_strings.index(best_full[0])
        return tracks[idx][2]

    # 2. Fallback to match track names only
    track_names = [track for track, artist, uri in tracks]
    best_track = process.extractOne(
        song_name,
        track_names,
        scorer=fuzz.token_sort_ratio
    )
    if best_track and best_track[1] > 60:
        idx = track_names.index(best_track[0])
        return tracks[idx][2]

    return None


def play_song_on_spotify(song_name):
    try:
        # Clean input (removes 'by', 'from', 'feat' to avoid confusion in query)
        cleaned = re.sub(r'\b(by|from|feat\.?)\b', ' ', song_name, flags=re.IGNORECASE).strip()
        # Build query using cleaned song_name
        query = f'track:"{cleaned}"'
        
        results = sp.search(q=query, type='track', limit=5)
        tracks = [(t['name'], t['artists'][0]['name'], t['uri']) for t in results['tracks']['items']]

        print(f"Input song_name: {song_name}")
        print(f"Parsed parts: {[cleaned]}")
        print(f"Spotify search query: {query}")
        print(f"Spotify search results count: {len(tracks)}")
        print(f"Tracks found: {[f'{t[0]} by {t[1]}' for t in tracks]}")

        if not tracks:
            print(f"No direct results for: {song_name}")
            return False

        track_uri = fuzzy_match_song(song_name, tracks)
        if track_uri:
            devices = sp.devices().get('devices', [])
            if devices:
                sp.start_playback(device_id=devices[0]['id'], uris=[track_uri])
                return True
            print("No active Spotify devices found")
            return False

        print(f"Close match not found for: {song_name}")
        return False

    except Exception as e:
        print(f"Playback failed: {e}")
        return False


# Function to pause Spotify
def pause_spotify():
    try:
        playback_state = sp.current_playback()
        
        if not playback_state or not playback_state['is_playing']:
            return False
        sp.pause_playback()
        return True
    except Exception as e:
        print(f"Pause failed: {e}")
        return False

# Function to resume Spotify
def resume_spotify():
    try:
        sp.start_playback()
        return True
    except Exception as e:
        print(f"Resume failed: {e}")
        return False

def next_track():
    try:
        sp.next_track()
        return True
    except Exception as e:
        print(f"Next track failed: {e}")
        return False

def previous_track():
    try:
        sp.previous_track()
        return True
    except Exception as e:
        print(f"Previous track failed: {e}")
        return False

# Function to play liked songs on shuffle
def play_liked_songs_on_shuffle(shuffle=True):
    try:
        sp.shuffle(state=shuffle)
        results = sp.current_user_saved_tracks(limit=50)
        uris = [item['track']['uri'] for item in results['items']]
        if uris:
            sp.start_playback(uris=uris)
            return True
        else:
            print("No liked songs found.")
            return False
    except Exception as e:
        print(f"Playing liked songs failed: {e}")
        return False

# Function to play a playlist
def play_playlist(playlist_name, shuffle=True):
    try:
        # Handle liked songs special case
        if playlist_name == "liked_songs":
            return play_liked_songs_on_shuffle(shuffle)
            
        # Regular playlist handling
        playlists = sp.current_user_playlists()['items']
        playlist_uri = None
        
        # Fuzzy match with lowercase comparison
        target = playlist_name.lower()
        for playlist in playlists:
            if target in playlist['name'].lower():
                playlist_uri = playlist['uri']
                break

        if playlist_uri:
            # Set shuffle state before playback
            sp.shuffle(shuffle)
            sp.start_playback(context_uri=playlist_uri)
            return True
            
        print(f"Playlist '{playlist_name}' not found in Spotify library.")
        return False
        
    except Exception as e:
        print(f"Playlist playback failed: {e}")
        return False







"""                    elif "play my liked songs on" in transcript.lower() or "play my like songs on" in transcript.lower() and "spotify" in transcript.lower():
                        say("Playing liked songs.")
                        play_liked_songs_on_shuffle()
                        break

                    if "play" in transcript.lower() and "spotify" in transcript.lower():
                        song = transcript.lower().replace("play", "").replace("on spotify", "").strip()
                        if song:
                            say(f"Playing {song} on Spotify.")
                            play_song_on_spotify(song)
                        else:
                            say("Please specify a song to play.")
                        break

                    elif "pause spotify" in transcript.lower():
                        say("Paused Spotify.")
                        pause_spotify()
                        break

                    elif "resume spotify" in transcript.lower():
                        say("Resumed Spotify.")
                        resume_spotify()
                        break

                    elif "next song" in transcript.lower() or "skip track" in transcript.lower():
                      next_track()
                      break

                    elif "previous song" in transcript.lower() or "go back" in transcript.lower():
                     previous_track()
                     break

                    if "play playlist" in transcript and "spotify" in transcript:
                        playlist_name = transcript.replace("play playlist", "").replace("on spotify", "").strip()
                        if playlist_name:
                            say(f"Playing playlist {playlist_name} on Spotify.")
                            play_playlist(playlist_name)  
                        else:
                            say("Please specify a playlist to play.")
                        break

                    elif transcript.lower().startswith("play ") and "spotify" not in transcript.lower() and "youtube" not in transcript.lower():
                      song = transcript.replace("play", "").strip()
                      if song:
                       ask_where_to_play(song)
                      else:
                        say("Please specify what you want to play.")
                        break
"""