#!/usr/bin/env python3

# built-in and third-party libs
import os
import sys
import time
from os.path import exists

import click
import psutil
import requests

# custom libs
from core import current_dir_path_export

current_dir_path_export()

from custom_modules.cfg import bootstrap
from custom_modules.logging.logging import log


@click.command()
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["demo", "live"], case_sensitive=False),
    help="Choose the run mode of the software",
)
@click.option("--version", is_flag=True, help="Show the version of the software", required=False)
def main(version, mode):
    """\b
    \b#################################################################################
    \b###                          🔸 RYBKACORE Software 🔸                         ###
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

    def TMP_folder(folder):
        if os.path.isdir(folder) is False:
            try:
                os.makedirs(folder)
            except Exception as e:
                log.FATAL_7(f"Attempt to create local folder [{folder}] - FAILED with error:\n{e}")

    TMP_folder("TEMP")

    kill_secondary_start_of_bot = False
    if exists("TEMP/pid_rybkaTmp") and os.stat("TEMP/pid_rybkaTmp").st_size != 0:
        with open("TEMP/pid_rybkaTmp", "r", encoding="utf8") as f:
            previous_pID = int(f.read())
            if psutil.pid_exists(previous_pID) and "python" in psutil.Process(previous_pID).name():
                kill_secondary_start_of_bot = True

    process_pid = os.getpid()
    if kill_secondary_start_of_bot:
        log.ORANGE(
            f" 🔮 Rybka bot is already running in this workspace [PID:{previous_pID}].\n 🔪 Killing current run [PID:{process_pid}]!"
        )
        psutil.Process(process_pid).kill()

    log.DEBUG(f"Allocating PID [{process_pid}]\n")

    with open("TEMP/pid_rybkaTmp", "w", encoding="utf8") as z:
        z.write(str(process_pid))
    time.sleep(1)

    core_runs = 0
    with open("TEMP/core_runsTmp", "w", encoding="utf8") as y:
        y.write(str(core_runs))
    time.sleep(1)

    if not version and not mode:
        click.echo(click.get_current_context().get_help())
        sys.exit(0)

    if version:
        print(f"🔍 RybkaCore Software Version  ➜  [{bootstrap.__version__}]")
        sys.exit(0)

    if mode:
        while True:
            core_runs += 1
            log.DEBUG(f"Run nr. [{core_runs}] of RybkaCore Software\n\n")
            with open("TEMP/core_runsTmp", "w", encoding="utf8") as x:
                x.write(str(core_runs))
            log.ORANGE("\n\n 📡 RybkaCore bot is being started...\n\n")
            time.sleep(2)

            status = os.system(f"python3 core.py -m {mode.upper()} --head")

            # 111 is a 'click' lib related stoppage
            if status == 111:
                break
            elif status == 2:
                log.FATAL(
                    f" 🔴 Rybka bot errored out with code [{status}],\n\nWhich is user stoppage. Shutting down Rybka."
                )
            elif status == 1792:
                log.FATAL(
                    f" 🔴 Rybka bot errored out with code [{status}].\n\nShutting down Rybka, it seems your API Key is either outdated or it doesn't have the permissions for [Spot & Margin Trading] enabled on it"
                )
            elif status == 7:
                log.FATAL(
                    f" 🔴 Rybka bot errored out with code [{status}].\n\nExit code '7' is a custom-set exit code within bot's mechanics. Manual action is required, Rybka is stopped."
                )
            else:
                log.WARN(
                    f" 🟠 Rybka bot errored out with code [{status}], which is not a custom-hard-coded one. Proceeding to check internet availability..."
                )
                while True:
                    log.INFO(" ")
                    log.INFO(" 🟣 Checking internet connection")
                    try:
                        r = requests.get("https://www.google.com")
                        log.INFO(
                            f" 🟢 🔌 Could ping Google servers, internet should be on - response [{r.status_code}] returned"
                        )
                        time.sleep(5)
                        log.INFO(" 🟢 Restart action sent.")
                        break
                    except Exception:
                        log.WARN(" 🟠 🔌 Internet seems to not be available")
                        log.INFO(" 🟣 Waiting 15 seconds and trying again")
                        time.sleep(15)
                    runs += 1
                    if running_in_ci and runs == 3:
                        log.FATAL(
                            " 🔴 This is a CI run. Breaking the process now after the 3 attempts."
                        )


if __name__ == "__main__":
    main()
