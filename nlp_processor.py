#nlp_processor.py
import re
from commands import COMMAND_MAP 
from thefuzz import fuzz,process

class NLPProcessor:
    def __init__(self):
            self.context = {
            "last_song": None,
            "conversation": [],  # Added missing key
            "last_intent": None  # Added missing key
        }

    def parse_command(self, transcript):
        transcript = transcript.lower().strip()
        self.context["conversation"].append(transcript)  # Track conversation

        if self._is_follow_up(transcript):
            return {
                "intent": "ai_followup", 
                "action": "handle_ai",
                "raw_text": transcript  
            }
        
        # Check AI queries first with priority matching
        ai_triggers = COMMAND_MAP["ai_query"]["triggers"]
        for trigger in ai_triggers:
            if fuzz.partial_ratio(trigger, transcript) > 85:
                return {
                    "intent": "ai_query",
                    "action": "handle_ai",
                    "raw_text": transcript
                }
        
        # Then check other commands (excluding AI queries that were already checked)
        for intent, data in COMMAND_MAP.items():
            if intent == "ai_query":  # Skip AI queries as we already checked them
                continue
                
            for trigger in data["triggers"]:
                # Check partial ratio for better match
                if fuzz.partial_ratio(trigger, transcript) > 85:
                    return {
                        "intent": intent,
                        "action": data["action"],
                        "raw_text": transcript
                    }
        
        return None
    
    def _is_follow_up(self, transcript):
        """Detect follow-up questions using context"""
        follow_up_triggers = [
            "and", "also", "what about", "how about", 
            "can you explain more", "tell me more"
        ]
        
        # Check if previous interaction was AI query
        if self.context["last_intent"] == "ai_query":
            return any(trigger in transcript for trigger in follow_up_triggers) \
                   or transcript.startswith(("and ", "but ", "what ", "how "))
        return False

    def extract_details(self, command):
        if not command:
            return None
            
        details = {}
        text = command["raw_text"].lower()

        #Volume Control
        if command["intent"] == "volume":
            num_match = re.search(r'(\d{1,3})%?', text)
            if num_match:
                details["level"] = int(num_match.group(1))
            else:
                word_to_num = {
                    "zero": 0, "ten": 10, "twenty": 20, "thirty": 30,
                    "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
                    "eighty": 80, "ninety": 90, "hundred": 100,
                    "max": 100, "full": 100, "half": 50
                }
                for word, num in word_to_num.items():
                    if word in text:
                        details["level"] = num
                        break
                else:
                    if any(word in text for word in ["up", "increase", "higher", "louder","loud"]):
                        details["level"] = "+20"
                    elif any(word in text for word in ["down", "decrease", "lower", "quieter","fighter","twitter","quarter","quiet"]):
                        details["level"] = "-20"
                    else:
                        for word, num in word_to_num.items():
                            if word in text:
                                details["level"] = num
                                break
        
        #Playback Control
        elif command["action"] == "control_playback":
            if any(word in text for word in ["next", "skip"]):
                details["command"] = "next"
            elif any(word in text for word in ["previous", "back", "last","repeat", "repeat that", "play again"]):
                details["command"] = "previous"
            elif any(word in text for word in ["pause", "stop","shut"]):
                details["command"] = "pause"
            elif any(word in text for word in ["resume", "play", "continue"]):
                details["command"] = "resume"

        #Play/Search Music
        elif command["intent"] == "play_music":
            # Add exclusion for liked songs phrasing
            if any(word in text for word in ["my liked songs", "liked songs", "saved songs"]):
                return None  # Force fallthrough to playlist handling
                
            for trigger in COMMAND_MAP["play_music"]["triggers"]:
                text = text.replace(trigger, "").strip()
            platform = None
            if "on spotify" in text:
                platform = "spotify"
                text = text.replace("on spotify", "").strip()
            elif "on youtube" in text:
                platform = "youtube"
                text = text.replace("on youtube", "").strip()
                
            song = text.strip()
            if song:
                if song in ["it", "that"] and self.context["last_song"]:
                    details["song"] = self.context["last_song"]
                else:
                    details["song"] = song
                    self.context["last_song"] = song
                
                if platform:
                    details["platform"] = platform
                else:
                    details["platform"] = "spotify"

        # Playlist Handling
        elif command["intent"] == "play_playlist":
            text = command["raw_text"].lower()
            details["platform"] = "spotify"

            # Fuzzy match for "liked songs" variations
            liked_triggers = [
                "liked songs", "light songs", "like songs",
                "liked tracks", "saved songs", "my songs"
            ]
    
            # Find best match using partial ratio
            best_match, score = process.extractOne(text, liked_triggers, 
                                        scorer=fuzz.partial_ratio)
    
            if score > 80:
                details["name"] = "liked_songs"
                details["shuffle"] = True
                return details
            
            if any(trigger in text for trigger in liked_triggers):
                details["name"] = "liked_songs"
                details["shuffle"] = True
                return details
            
            # Extract for older liked songs check
            if any(word in text for word in ["liked", "saved", "my songs"]):
                details["name"] = "liked_songs"
                details["shuffle"] = True
                return details
            
            # Extract shuffle command
            details["shuffle"] = any(word in text for word in ["shuffle", "random"])
        
            # Remove trigger phrases
            triggers = COMMAND_MAP["play_playlist"]["triggers"]
            for trigger in triggers:
                text = text.replace(trigger, "").strip()
            
            details["name"] = text.strip()
        
        return details