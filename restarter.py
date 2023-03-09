#!/usr/bin/env python3

# built-in and third-party libs
import os
import time
import requests
import click


# custom libs
from rybka import current_dir_path_export
current_dir_path_export()

from custom_modules.logging.logging import log
from custom_modules.cfg import bootstrap



@click.command()
@click.option('--mode', '-m', type=click.Choice(['demo', 'live'], case_sensitive=False), help='Choose the run mode of the software')
@click.option("--version", is_flag=True, help = "Show the version of the software", required = False)
@click.option("--info", is_flag=True, help = "More info about 'restarter' add-on", required = False)
def main(version, mode, info):
    """\b
    \b#################################################################################
    \b###                            🔶 RYBKA Software 🔶                           ###
    \b###                       🔸 Rybka's restarter add-on 🔸                      ###
    \b###                                                                           ###
    \b###   📖 Docs: https://gitlab.com/Silviu_space/rybka/-/blob/master/README.md  ###
    \b#################################################################################
    \b###                                                                           ###
    \b###   🔹 Author:    ©️ Silviu-Iulian Muraru                                    ###
    \b###   🔹 Email:     silviumuraru90@yahoo.com                                  ###
    \b###   🔹 LinkedIn:  https://www.linkedin.com/in/silviu-muraru-iulian/         ###
    \b###                                                                           ###
    \b#################################################################################
    """

    running_in_ci = os.environ.get("CI", False)
    runs = 0

    if not version and not mode and not info:
        click.echo(click.get_current_context().get_help())
        exit(0)
    
    if version:
        print(f"🔍 Rybka Software Version  ➜  [{bootstrap.__version__}]")
        exit(0)

    if info:
        print(f"🔍 This 'restarter' add-on facilitates the restarting of Rybka trading bot whenever it fails due to unknown reasons or whether the internet is down for a period of time.")
        time.sleep(8)
        print(f"🔍 As Rybka exports the valuable information about its past transactions into files, restarter guarantees the job is re-started from where it got left, not losing information in the process!")
        time.sleep(11)
        print(f"🔍 It is recommended to always run Rybka through this 'restarter' module, as the uptime of the bot is much longer extended this way.")
        exit(0)

    if mode:
        while True:
            log.INFO(" 📡 Rybka bot is being started...")
            time.sleep(2)
            #######################################################################
            #             Change below line to: os.system("rybka")                #
            #######################################################################
            status = os.system(f"python3 rybka.py -m {mode.upper()}")
            # 111 is a click-related stoppage
            if status == 111:
                break
            elif status == 2:
                log.FATAL(f" 🔴 Rybka bot errored out with code [{status}],\n\nWhich is user stoppage. Closing both Rybka and Restarter.")
            elif status == 1792:
                log.FATAL(f" 🔴 Rybka bot errored out with code [{status}].\n\nClosing both Rybka and Restarter, it seems your API Key is outdated, make sure you update it / enable all permissions for it!")
            elif status == 7:
                log.FATAL(f" 🔴 Rybka bot errored out with code [{status}].\n\nExit code '7' is a custom-set exit code within bot's mechanics. Manual action is required, both Rybka and restarter module are stopped.")
            else:
                log.WARN(f" 🟠 Rybka bot errored out with code [{status}], which is not a custom-hard-coded one. Proceeding to check internet availability...")
                while True:
                    log.INFO(" ")
                    log.INFO(f" 🟣 Checking internet connection")
                    try:
                        r = requests.get("https://www.google.com")
                        log.INFO(f" 🟢 🔌 Could ping Google servers, internet should be on - response [{r.status_code}] returned")
                        time.sleep(5)
                        log.INFO(" 🟢 Restart action sent.")
                        break
                    except Exception as e:
                        log.WARN(" 🟠 🔌 Internet seems to not be available")
                        log.INFO(" 🟣 Waiting 15 seconds and trying again")
                        time.sleep(15)
                    runs+=1
                    if running_in_ci and runs == 3:
                        log.FATAL(" 🔴 This is a CI run. Breaking the process now after the 3 attempts.")
                

if __name__ == '__main__':
    main()
