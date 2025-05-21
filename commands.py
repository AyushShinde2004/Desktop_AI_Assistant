COMMAND_MAP = {
    "play_playlist": {
        "triggers": [
            "playlist", "play my liked songs", "play liked songs","light songs",
            "my like songs"
        ],
        "action": "play_playlist",
        "requires": ["name"]
    },
    "play_music": {
        "triggers": ["play", "start", "listen to"],
        "action": "play_music",
        "requires": ["song"]
    },
    "playback_control": {
        "triggers": [
            "next", "skip", "next song", "skip track",
            "previous", "back", "last song","repeat","again",
            "pause","resum", "stop","pause the song", "stop the music", "pause music", "stop song","shut","shut up", "shutup", 
            "resume", "play", "continue"
        ],
        "action": "control_playback",
        "requires": {"command": "str"} 
    },
    "volume": {
        "triggers": ["volume", "louder", "quieter","loud","quiet",
            "turn up", "turn down", "increase volume","make it",
            "decrease volume", "volume to", "set volume","movie", "night", "party","fighter","twitter","quarter"],
        "action": "set_volume",
        "requires": ["level"]
    },
    "natural_commands": {
        "triggers": [
            "hey", "okay", "alright", "so", "well", 
            "actually", "by the way", "anyway"
        ],
        "action": "continue_conversation"
    },
    "ai_query": {
        "triggers": [
            "what is", "who is", "explain", "tell me about",
            "how to", "why does", "what are", "can you tell",
            "would you explain", "could you describe"
        ],
        "action": "handle_ai",
        "requires": ["query"]
    }
}