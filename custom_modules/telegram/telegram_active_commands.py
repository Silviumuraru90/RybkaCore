#!/usr/bin/env python3


def sample_responses(input_text):
    user_message = str(input_text).lower()
    
    if user_message in ("who are you", "who are you?"):
        return "I am Rybka's Telegram bot!"
  
    return "Sorry, but I don't understand you! \nType '/help' for a list of supported commands."
