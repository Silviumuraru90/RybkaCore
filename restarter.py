#!/usr/bin/env python3

import os, time, requests

running_in_ci = os.environ.get("CI", False)
runs = 0

while True:
    print("Rybka bot is being started...")
    time.sleep(2)
    #######################################################################
    #             Change below line to: os.system("rybka")                #
    #######################################################################
    status = os.system("python3 rybka.py")
    if status == 7:
        print(f"\nRybka bot errored out with code {status}.\n\nExit code '7' is a custom-set exit code within bot's mechanics. Manual action is required, both Rybka and restarter module are stopped.")
        break
    else:
        print(f"\nRybka bot errored out with code {status}, which is not a custom-hard-coded one. Proceeding to check internet availability...")
        internet_down = False
        for i in range(1, 11):
            print(f"\nTesting internet. Attempt {i}/10")
            try:
                r = requests.get("https://www.google.com")
                print(f"\nCould ping Google servers, internet should be on - response [{r.status_code}] returned")
                time.sleep(5)
                break
            except Exception as e:
                internet_down = True
                print("Internet seems to not be available")
                print("Waiting 15 seconds and trying again")
                time.sleep(15)
        if not internet_down:
            print("\nRybka did not catch the internet connection as being down. Hence it might've been a different cause of failure")
            print("\nApplying a 1-minute break and will restart Rybka bot afterwards!")
            time.sleep(60)
        else:
            print("\nRestart action sent.")
    runs+=1
    if running_in_ci and runs == 3:
        print("\nThis is a CI run. Breaking the process now after the 3 attempts.")
        break
