from spotify_control import *
from selenium_controls import selenium_play_pause, selenium_next_video, play_on_youtube


last_platform = "spotify"  # Default platform

def handle_media_command(action, details):
    global last_platform
    try:
        details = details or {}

        song = details.get("song")
        platform = details.get("platform", "spotify")  # Default to Spotify

        if action == "play_music":
            if not song:
                print("Error: No song specified")
                return False

            if platform == "spotify":
                # If last platform was YouTube, pause it before playing Spotify
                if last_platform == "youtube":
                    selenium_play_pause()  # Pause YouTube if it was the last platform
                try:
                    success = play_song_on_spotify(song)
                    if success:
                        last_platform = "spotify"  # Update platform to Spotify
                    return success
                except Exception as e:
                    print(f"Spotify play error: {e}")
                    return False
                
            elif platform == "youtube":
                # If last platform was Spotify, pause it before playing YouTube
                if last_platform == "spotify":
                    pause_spotify()  # Pause Spotify if it was the last platform
                try:
                    success = play_on_youtube(song)
                    if success:
                        last_platform = "youtube"  # Update platform to YouTube
                    return success
                except Exception as e:
                    print(f"YouTube play error: {e}")
                    return False
            else:
                print(f"Invalid platform: {platform}")
                return False

        elif action == "control_playback":
            cmd = details.get("command")

            # Handle Spotify controls if the last platform was Spotify
            if last_platform == "spotify" and cmd in ["next", "previous", "pause", "resume"]:
                try:
                    if cmd == "next":
                        success = next_track()
                    elif cmd == "previous":
                        success = previous_track()
                    elif cmd == "pause":
                        success = pause_spotify()
                    elif cmd == "resume":
                        success = resume_spotify()

                    if success:
                        return True
                except Exception as e:
                    print(f"Spotify control failed: {e}")

            # Handle YouTube controls if the last platform was YouTube
            if last_platform == "youtube":
                if cmd == "next":
                    return selenium_next_video()  # Handle YouTube next
                elif cmd in ["pause", "resume"]:
                    return selenium_play_pause()  # Handle YouTube pause/resume
                elif cmd == "previous":
                    print("Can't rewind YouTube videos")
                    return False

            print(f"Command not valid for current platform: {cmd}")
            return False

        # Playlist handling
        elif action == "play_playlist":
            name = details.get("name", "")
            shuffle = details.get("shuffle", True)

            if name == "liked_songs":
                success = play_liked_songs_on_shuffle(shuffle)
            else:
                success = play_playlist(name, shuffle)

            if success:
                last_platform = "spotify"  # Update platform to Spotify
            return success

    except Exception as e:
        print(f"Media control error: {e}")
        # Fallback to YouTube if Spotify fails
        if action == "play_music" and details.get("platform") == "spotify":
            print("Attempting YouTube fallback...")
            return play_on_youtube(details["song"])
        return False