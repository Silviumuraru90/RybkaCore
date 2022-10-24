#!/usr/bin/env python3

# Built-in and Third-Party Libs
import GPUtil
import json
import psutil


def sample_responses(input_text):
    user_message = str(input_text).lower()
    
    if user_message in ("who are you", "who are you?"):
        return "I am Rybka's telegram bot!"

    elif user_message in ("gpu temp", "gpu", "gpu temperature"):
        # Works for Nvidia GPUs
        # Need to determine for Intel, AMD and Broadcom
        return f"GPU Temp is {GPUtil.getGPUs()[0].temperature}" + u'\xb0' + "C"

    elif user_message in ("alive", "awake", "status"):
        with open(f"TEMP/pidTmp", 'r', encoding="utf8") as f:
            pID = json.loads(f.read())
            if psutil.pid_exists(pID):
                status = "Bot is alive and well, no worries! \nGive yourself a pat on the back! \nRelax and stay hydrated!"
            else:
                status = "Bot is stopped. Help it get back on track! \nC'mon! Results, not excuses!"
        return status

    if user_message in ("/help", "help", "help?", "help!", "command", "/command", "commands", "/commands"):
        return f"""Available commands are:

FUN commands:
    {'who are you?':20} - Who is the account you are talking to?

FUNctional commands:
    {'status':20}        - Check Rybka software's status
    {'gpu temp':20}   - Shows PC's GPU temperature
        """
        
    return "Sorry, but I don't understand you! \nType 'help' for a list of supported commands."
