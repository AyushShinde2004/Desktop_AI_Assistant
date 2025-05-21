# gemini_handler.py
from datetime import datetime

class GeminiHandler:
    def __init__(self, gemini_func, weather_func):
        self.gemini = gemini_func
        self.weather = weather_func
        self.context = {
            "last_query": None,
            "conversation": []
        }

    def process_input(self, transcript):
        try:
            cleaned = transcript.lower().strip()

            # Maintain conversation history
            self.context["conversation"].append({"user": cleaned})
            
            # Get Gemini response with context
            response = self.gemini({
                "query": cleaned,
                "history": self.context["conversation"][-3:]  # Last 3 exchanges
            })
            
            # Handle API errors
            if isinstance(response, str) and response.startswith("Error"):
                return "Sorry, I'm having trouble with that. Could you try again?"
            
            # Store context
            self.context["last_query"] = cleaned
            self.context["conversation"].append({"assistant": response})
            
            return self._naturalize_response(response)
            
        except Exception as e:
         print(f"GeminiHandler Error: {e}")  # Add this
         return "Something went wrong. Let's try that again."
        
    def _naturalize_response(self, response):
        """Make responses more conversational"""
        if not response:
            return ""

        replacements = {
            "Here is": "Sure! Here's",
            "Answer:": "I found this:",
            "According to": "From what I know,",
            "The answer is": "I think it's",
            "**": ""  # Remove markdown formatting
        }

        for key, value in replacements.items():
            response = response.replace(key, value)

        # Strip extra whitespace
        response = response.strip()

        # Capitalize first letter if needed
        if response and not response[0].isupper():
            response = response[0].upper() + response[1:]

        # Ensure it ends with proper punctuation
        if response and response[-1] not in '.!?':
            response += '.'

        return response
