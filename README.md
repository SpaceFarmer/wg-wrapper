# wg-wrapper
Wrapper around [wireguard-tools](https://www.wireguard.com/install/) with the intention to make it easier to handle multiple tunnels simultaneously.

<img src="https://github.com/SpaceFarmer/wg-wrapper/assets/12208962/15cc6618-ce04-4f26-8e9f-11cbe5d3faff" width=40% height=40%>

## Functions

### Options
| Option        | What it does                                                                  |
|---------------|-------------------------------------------------------------------------------|
| --help        | Show help message                                                             |
| --list        | List all currently active tunnels wireguard tunnels defined in wg_config_path |
| --configfiles | List all the wg-configfiles found in wg_config_path                           |
| --start       | This will start all wg-tunnels that we find config files for in wg_config_path|
| --kill        | This will kill all active wg-tunnels we find config files for in wg_config_path|
| --generate    | Generate new WireGuard keys for use in new tunnel config                      |
| --debug       | Print debug oriented output (private keys will be printed)                    |

### Exceptions in config.ini
If you have lots of tunnels and tunnel configurations and for some reason dont want to start all or kill all with the `--start` or `--kill` options, there is a way to exclude those in the `config.ini`.
* `StartAllTunnelsExceptions =` A comma separated list of config-file names
* `KillAllTunnelsExceptions =` A comma separeted list of config-file names

## Pre-req's
* Have `wireguard-tools` installed
* Have a supported python3 version installed
* This is only tested on macOS

## How to use
* Clone the repo or download the files needed (`wg-wrapper.py` and `config.ini`)
* Make sure the `WireGuardConfigFilesPath` in `config.ini` matches the path for your config files. Supported paths can be found by running the command `wg-quick`
* Execute by running `wg-wrapper.py --<option>` in the terminal

### Optional
* Add the wg-wrapper to "path" for ease of execution. Alternativly add an alias that points to the script:
    * Example: `alias wg-wrapper="/Users/username/wg-wrapper/wg-wrapper.py"`
