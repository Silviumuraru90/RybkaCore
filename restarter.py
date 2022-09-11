import os, time, requests

while True:
    print("Rybka bot is being started...")
    time.sleep(2)
    #######################################################################
    #             Change below line to: os.system("rybka")                #
    #######################################################################
    status = os.system("python rybka.py")
    if status == 7:
        print(f"\nRybka bot errored out with code {status}.\n\nExit code '7' is a custom-set exit code within bot's mechanics. Manual action is required, both Rybka and restarter module are stopped.")
        break
    else:
        print(f"\nRybka bot errored out with code {status}. Checking internet availability...")
        for i in range(1, 2):
            print(f"\nTesting internet. Attempt {i}/10")
            try:
                r = requests.get("https://www.google.com")
                print(f"\nCould ping Google servers, internet should be on - response [{r.status_code}] returned")
                time.sleep(5)
                break
            except Exception as e:
                print("Internet seems to not be available")
                print("Waiting 15 seconds and trying again")
                time.sleep(15)
        print("\n\nBot might be able to be restarted at this point.")
        print("\n\nWill restart Rybka bot in 1 minute")
        time.sleep(60)
