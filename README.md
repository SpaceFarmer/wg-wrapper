# wg-wrapper
Wrapper around wireguard-tools

## Functions

### Options
| Option        | What it does                                                  |
|---------------|---------------------------------------------------------------|
| --help        | Show help message                                             |
| --list        | List all currently active tunnels wireguard tunnels           |
| --configfiles | List all the wg-configfiles found in wg_config_path           |
| --start       | This will start all wg-tunnels that we find config files for  |
| --kill        | This will kill all active wg-tunnels                          |
| --generate    | Generate new WireGuard keys for use in new tunnel config      |
| --debug       | Print debug oriented output (private keys will be printed)    |

### Exceptions in config.ini
If you have lots of tunnels and tunnel configurations and for some reason dont want to start all or kill all with the `--start` or `--kill` options, there is a way to exclude those in the `config.ini`.
* `StartAllTunnelsExceptions =` A comma separated list of config-file names
* `KillAllTunnelsExceptions =` A comma separeted list of config-file names

## Pre-req's
* Have wg-tools installed
* Have a supported python3 version installed
* This is only tested on macOS

## How to use
* Clone the repo or download the files needed (`wg-wrapper.py` and `config.ini`)
* Make sure the `WireGuardConfigFilesPath` in `config.ini` matches the path for your config files
* Execute by running `wg-wrapper.py --<option>` in the terminal

### Optional
* Add the wg-wrapper to "path" for ease of execution. Alternativly add an alias that points to the script:
    * Example: `alias wg-wrapper="/Users/username/wg-wrapper/wg-wrapper.py"`