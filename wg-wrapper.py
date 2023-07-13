#!/usr/bin/env python3
# pylint: disable=invalid-name
# pylint: enable=invalid-name

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


def parse_wg_config_files(wg_config_path: str, debug: bool):
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
                with open(filename.path, "r", encoding='UTF-8') as file:
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

    return wg_peers_dict, config_files


def list_active_tunnels(wg_peers_dict: dict, config_files: list) -> None:
    """This function prints all currently active tunnels on screen"""
    print(f"\n{Bcolors.OKCYAN}=== The following peers are active ==={Bcolors.ENDC}\n")
    if len(wg_peers_dict) > 1:
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


def kill_active_tunnels(wg_peers_dict: dict, config_files: list) -> None:
    """This function kills all currently active tunnels"""
    print(f"\n{Bcolors.OKCYAN}===Kill all active tunnels==={Bcolors.ENDC}\n")
    if len(wg_peers_dict) > 1:
        for active_peer in wg_peers_dict:
            for file in config_files:
                if wg_peers_dict[active_peer] == file["Peer"]["publickey"]:
                    # Get the first part of the filename (whithout .conf)
                    file_shortname = file["filename"].split(".", 1)[0]
                    print(f"==Killing tunnel: {file_shortname}==")
                    subprocess.check_output(
                        f"sudo wg-quick down {file_shortname}", shell=True
                    ).decode("utf-8")
    else:
        print("No active VPN peers was found")
    print(f"\n{Bcolors.OKCYAN}============================={Bcolors.ENDC}")


def start_all_tunnels(wg_peers_dict: dict, config_files: list) -> None:
    """This function starts all tunnels that there is config for in wg_config_path"""
    print(f"\n{Bcolors.OKCYAN}=== Start all tunnels ==={Bcolors.ENDC}")
    if len(wg_peers_dict) >= len(config_files):
        print("\nAll tunnels are already started")
    elif len(wg_peers_dict) < len(config_files):
        for file in config_files:
            # for active_peer in wg_peers_dict:
            if file["Peer"]["publickey"] not in wg_peers_dict.values():
                file_shortname = file["filename"].split(".", 1)[0]
                print(f"\nStarting tunnel: {file_shortname}")
                subprocess.check_output(
                    f"sudo wg-quick up {file_shortname}", shell=True
                ).decode("utf-8")
            elif file["Peer"]["publickey"] in wg_peers_dict.values():
                print(f"Tunnel for file is already started: {file['filename']}")
            else:
                print(
                    f"Something went wrong when trying to start tunnel for: {file['filename']}"
                )
                raise SystemExit(1)
    print(f"\n{Bcolors.OKCYAN}========================={Bcolors.ENDC}")


def main() -> None:
    """The starting point of the program"""

    # This clas gives you the full help message when supplying a faulty argument
    class MyParser(argparse.ArgumentParser):
        """Class to provide full help message when supplying a faulty argument"""
        def error(self, message):
            sys.stderr.write(f"error: {message}\n")
            self.print_help()
            sys.exit(2)

    msg = "This is a wrapper arround wireguard-tools with the listed options below:"
    parser = MyParser(description=msg, prog="wg-wrapper")
    parser.add_argument(
        "-l", "--list", action="store_true", help="List all currently active tunnels"
    )
    parser.add_argument(
        "-s",
        "--start",
        action="store_true",
        help="Start all tunnels in the wg_config_path",
    )
    parser.add_argument(
        "-k",
        "--kill",
        action="store_true",
        help="Kill all active tunnels defined in wg_config_path",
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

    # Path to the WG config files, change this if your config files are stores elsewhere
    wg_config_path = "/opt/homebrew/etc/wireguard"

    if os.path.isdir(wg_config_path):
        # Parse the wg configfiles and get currently active peers used in the other functions
        wg_peers_dict, config_files = parse_wg_config_files(wg_config_path, args.debug)
    else:
        print(
            f"{Bcolors.FAIL}The path defined for wg config-files does not exist: {wg_config_path}{Bcolors.ENDC}"
        )
        sys.exit(1)

    # Call the different functions depending on supplied argunements
    if args.list:
        list_active_tunnels(wg_peers_dict, config_files)
    if args.start:
        start_all_tunnels(wg_peers_dict, config_files)
    if args.kill:
        kill_active_tunnels(wg_peers_dict, config_files)


if __name__ == "__main__":
    main()
