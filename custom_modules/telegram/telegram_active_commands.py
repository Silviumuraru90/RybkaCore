#!/usr/bin/env python3


def sample_responses(input_text):
    user_message = str(input_text).lower()

    if user_message in ("who are you?!"):
        return """I am RybkaCore bot!

        - I'm an Open Source Crypto Trading bot that trades the EGLD-USDT pair
        - Designed to work on Binance
        - Per RC release updates (starting with 0.8.19-RC), bot may very well surpass 100% ROI Y2Y, if the best-practices in README.md are followed through and market doesn't go into an ATH phase

        Let automation take your crypto-wallet to the next level!
        """

    return "Sorry, but I don't understand you! \nType '/help' for a list of supported commands."
