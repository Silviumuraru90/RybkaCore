#!/usr/bin/env python3


def sample_responses(input_text):
    user_message = str(input_text).lower()
    
    if user_message in ("who are you", "who are you?", "who are you?!"):
        return """I am Rybka bot!

        - I'm an Open Source Crypto Trading bot that works primarily on EGLD-USDT
        - Designed to work on Binance
        - Per beta tests: Y2Y ROI of ~80-120% (for now 😉)

        Let automation take your crypto-wallet to the next level!
        """
  
    return "Sorry, but I don't understand you! \nType '/help' for a list of supported commands."
