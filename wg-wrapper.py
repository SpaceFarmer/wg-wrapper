#!/usr/bin/env python3
# pylint: disable=invalid-name
# pylint: enable=invalid-name
"""python wrapper around wg-tools"""

import argparse
import configparser
import os
import pprint
import subprocess
import sys


# Define color codes
class Bcolors:
    """Class to allow for custom colors in print statements"""

    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"


def get_wg_peers(debug: bool) -> dict:
    """This function returns a dict of all currently active VPN-peers"""
    # Get active WG peers
    active_wg_peers = subprocess.check_output(
        "sudo wg show all peers", shell=True
    ).decode("utf-8")
    active_wg_peers_list = active_wg_peers.split()
    if debug:
        print(
            f"\n{Bcolors.WARNING}DEBUG: list active peers from (wg show all peers):{Bcolors.ENDC}\n{active_wg_peers}"
        )

    # Create a dict with the active wg peers using the utun interface as key and pub-key as value.
    # This is used in other functions to be able to list, include and exclude active peers.
    wg_peers_dict = {}
    i = 0
    while i < len(active_wg_peers_list):
        wg_peers_dict[active_wg_peers_list[i]] = active_wg_peers_list[i + 1]
        i = i + 2
    if debug:
        print(
            f"\n{Bcolors.WARNING}DEBUG: wg_peers_dict content:\n{wg_peers_dict}{Bcolors.ENDC}"
        )

    return wg_peers_dict


def parse_wg_config_files(wg_config_path: str, debug: bool) -> list:
    """This function parses wg-config files and creates a dict of currently active VPN-peers"""
    # Parse wg config files
    config_files = []
    for filename in os.scandir(wg_config_path):
        if filename.is_file():
            if ".conf" in filename.name:
                if debug:
                    print(
                        f"\n{Bcolors.WARNING}DEBUG: found the following filename: {filename.name}{Bcolors.ENDC}"
                    )
                config_object = configparser.ConfigParser()
                with open(filename.path, "r", encoding="UTF-8") as file:
                    config_object.read_file(file)
                    output_dict = {
                        s: dict(config_object.items(s))
                        for s in config_object.sections()
                    }
                    output_dict["filename"] = filename.name
                    config_files.append(output_dict)

    # Print the parsed configfiles
    if debug:
        for file in config_files:
            print(f"\n{Bcolors.WARNING}DEBUG: The output dictionary is:{Bcolors.ENDC}")
            p_print = pprint.PrettyPrinter(indent=4, depth=2)
            p_print.pprint(file)

    return config_files


def list_active_tunnels(wg_peers_dict: dict, config_files: list) -> None:
    """This function prints all currently active tunnels on screen"""
    print(f"\n{Bcolors.OKCYAN}=== The following peers are active ==={Bcolors.ENDC}\n")
    if len(wg_peers_dict) >= 1:
        for active_peer in wg_peers_dict:
            for file in config_files:
                if wg_peers_dict[active_peer] == file["Peer"]["publickey"]:
                    print(f"Filename: {file['filename']}")
                    print(f"Endpoint: {file['Peer']['endpoint']}")
                    print(f"PubKey: {file['Peer']['publickey']}")
                    print(f"Interface name: {active_peer}\n")
    else:
        print("No active VPN peers was found\n")
    print(f"{Bcolors.OKCYAN}======================================{Bcolors.ENDC}")


def kill_active_tunnels(
    wg_peers_dict: dict, config_files: list, kill_exceptions_list: list
) -> None:
    """This function kills all currently active tunnels"""
    print(f"\n{Bcolors.OKCYAN}===Kill all active tunnels==={Bcolors.ENDC}\n")
    if len(wg_peers_dict) >= 1:
        for active_peer in wg_peers_dict:
            for file in config_files:
                if wg_peers_dict[active_peer] == file["Peer"]["publickey"]:
                    # Exlude exceptions found in config.ini
                    if file["filename"] not in kill_exceptions_list:
                        # Get the first part of the filename (whithout .conf)
                        file_shortname = file["filename"].split(".", 1)[0]
                        print(f"==Killing tunnel: {file_shortname}==")
                        subprocess.check_output(
                            f"sudo wg-quick down {file_shortname}", shell=True
                        ).decode("utf-8")
                    else:
                        print(
                            f"\n{Bcolors.WARNING}Excepted tunnel config found, not killing: {file['filename']}{Bcolors.ENDC}"
                        )
    else:
        print("No active VPN peers was found")
    print(f"\n{Bcolors.OKCYAN}============================={Bcolors.ENDC}")


def start_all_tunnels(
    wg_peers_dict: dict, config_files: list, start_exceptions_list: list
) -> None:
    """This function starts all tunnels that there is config for in wg_config_path"""
    print(f"\n{Bcolors.OKCYAN}=== Start all tunnels ==={Bcolors.ENDC}")
    if len(wg_peers_dict) >= len(config_files):
        print("\nAll tunnels are already started")
    elif len(wg_peers_dict) < len(config_files):
        for file in config_files:
            # for active_peer in wg_peers_dict:
            if file["Peer"]["publickey"] not in wg_peers_dict.values():
                # Exlude exceptions found in config.ini
                if file["filename"] not in start_exceptions_list:
                    file_shortname = file["filename"].split(".", 1)[0]
                    print(f"\nStarting tunnel: {file_shortname}")
                    try:
                        subprocess.check_output(
                            f"sudo wg-quick up {file_shortname}", shell=True
                        ).decode("utf-8")
                    except subprocess.CalledProcessError as e:
                        print(
                            f"{Bcolors.FAIL}Error occured while trying to start tunnel: {file_shortname}{Bcolors.ENDC}"
                        )
                        print(
                            f"{Bcolors.FAIL}Error returncode: {e.returncode}{Bcolors.ENDC}"
                        )
                else:
                    print(
                        f"\n{Bcolors.WARNING}Excepted tunnel config found, not starting: {file['filename']}{Bcolors.ENDC}"
                    )
            elif file["Peer"]["publickey"] in wg_peers_dict.values():
                print(f"Tunnel for file is already started: {file['filename']}")
            else:
                print(
                    f"Something went wrong when trying to start tunnel for: {file['filename']}"
                )
                raise SystemExit(1)
    print(f"\n{Bcolors.OKCYAN}========================={Bcolors.ENDC}")


def list_wg_configfiles(config_files: list, wg_config_path: str) -> None:
    """Print the config files in wg_config_path"""
    print(f"\n{Bcolors.OKCYAN}===List all wg-config files==={Bcolors.ENDC}\n")
    print(f"wg config-file path: {wg_config_path}")
    if len(config_files) > 0:
        for file in config_files:
            print(f'{file["filename"]}')
    else:
        print("No active VPN peers was found")
    print(f"\n{Bcolors.OKCYAN}=============================={Bcolors.ENDC}")


def generate_wg_keys(wg_config_path: str) -> None:
    """Generates wg keys for use in a new wg tunnel"""
    print(f"\n{Bcolors.OKCYAN}===Generate new WireGuard keys==={Bcolors.ENDC}\n")
    print("Generating public and private keys for new wg-tunnel config...")

    # Warn if files already exists
    yes_choices = ["yes", "y"]
    no_choices = ["no", "n"]
    if os.path.isfile(f"{wg_config_path}/public.key"):
        print(
            f"{Bcolors.WARNING}Public key file already exists, continue and overwrite existing file?{Bcolors.ENDC} {wg_config_path}/public.key"
        )
        while True:
            user_input = input("Overwrite y/n? ")
            if user_input.lower() in yes_choices:
                print("Continuing...")
                break
            if user_input.lower() in no_choices:
                print("Aborting key-generation...")
                sys.exit(1)
            else:
                print('Invalid input, type "y" or "n"')
                continue
    if os.path.isfile(f"{wg_config_path}/private.key"):
        print(
            f"{Bcolors.WARNING}Private key file already exists, continue and overwrite existing file?{Bcolors.ENDC} {wg_config_path}/private.key"
        )
        while True:
            user_input = input("Overwrite y/n? ")
            if user_input.lower() in yes_choices:
                print("Continuing...")
                break
            if user_input.lower() in no_choices:
                print("Aborting key-generation...")
                sys.exit(1)
            else:
                print('Invalid input, type "y" or "n"')
                continue

    # Generate a new public and private wg-key and make sure only the user has permissions on the files
    subprocess.check_output(
        f"umask 077 && wg genkey | tee {wg_config_path}/private.key | wg pubkey > {wg_config_path}/public.key",
        shell=True,
    )

    print("The keys are now generated and located here:")
    if os.path.isfile(f"{wg_config_path}/public.key"):
        print(f"{wg_config_path}/public.key")
    else:
        print(
            f"{Bcolors.FAIL}The file with the public key could not be found: {wg_config_path}/public.key{Bcolors.ENDC}"
        )
        sys.exit(1)
    if os.path.isfile(f"{wg_config_path}/private.key"):
        print(f"{wg_config_path}/private.key")
    else:
        print(
            f"{Bcolors.FAIL}The file with the private key could not be found: {wg_config_path}/private.key{Bcolors.ENDC}"
        )
        sys.exit(1)

    print(f"\n{Bcolors.OKCYAN}================================={Bcolors.ENDC}")


def main() -> None:
    """The starting point of the program"""

    # This class gives you the full help message when supplying a faulty argument
    class MyParser(argparse.ArgumentParser):
        """Class to provide full help message when supplying a faulty argument"""

        def error(self, message):
            sys.stderr.write(f"error: {message}\n")
            self.print_help()
            sys.exit(2)

    msg = "This is a wrapper around wireguard-tools with the listed options below:"
    parser = MyParser(description=msg, prog="wg-wrapper")
    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="List all currently active tunnels defined in wg_config_path",
    )
    parser.add_argument(
        "-c",
        "--configfiles",
        action="store_true",
        help="List all configfiles in wg_config_path",
    )
    parser.add_argument(
        "-s",
        "--start",
        action="store_true",
        help="Start all tunnels defined in wg_config_path",
    )
    parser.add_argument(
        "-k",
        "--kill",
        action="store_true",
        help="Kill all active tunnels defined in wg_config_path",
    )
    parser.add_argument(
        "-g",
        "--generate",
        action="store_true",
        help="Generete new wg keys for use in new tunnel config",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Print debug oriented output (private keys will be printed)",
    )
    args = parser.parse_args()

    # Print full help message when no arguments are supplied
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Get the path for the script beeing executed
    script_dir = os.path.dirname(__file__)
    # Read contents of config.ini
    if os.path.isfile(f"{script_dir}/config.ini"):
        config = configparser.ConfigParser()
        config.read(f"{script_dir}/config.ini")
        # Get the path to tunnel config files
        wg_config_path = config["DEFAULT"]["WireGuardConfigFilesPath"]
        # Get tunnel "start all" exceptions
        start_exceptions = (config["EXCEPTIONS"]["StartAllTunnelsExceptions"]).replace(
            " ", ""
        )
        start_exceptions_list = start_exceptions.split(",")
        # Get tunnel "kill all" exceptions
        kill_exceptions = (config["EXCEPTIONS"]["KillAllTunnelsExceptions"]).replace(
            " ", ""
        )
        kill_exceptions_list = kill_exceptions.split(",")
    else:
        print(f"{Bcolors.FAIL}Could not find the config.ini file{Bcolors.ENDC}")
        sys.exit(1)

    # Get all active wg-peers
    wg_peers_dict = get_wg_peers(args.debug)

    if os.path.isdir(wg_config_path):
        # Parse the wg configfiles and get currently active peers used in the other functions
        config_files = parse_wg_config_files(wg_config_path, args.debug)
    else:
        print(
            f"{Bcolors.FAIL}The path defined for wg config-files does not exist: {wg_config_path}{Bcolors.ENDC}"
        )
        sys.exit(1)

    # Call the different functions depending on supplied argunements
    if args.list:
        list_active_tunnels(wg_peers_dict, config_files)
    if args.start:
        start_all_tunnels(wg_peers_dict, config_files, start_exceptions_list)
    if args.kill:
        kill_active_tunnels(wg_peers_dict, config_files, kill_exceptions_list)
    if args.configfiles:
        list_wg_configfiles(config_files, wg_config_path)
    if args.generate:
        generate_wg_keys(wg_config_path)


if __name__ == "__main__":
    main()
