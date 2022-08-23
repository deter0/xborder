# xborders
Active window border replacement for window managers.

## Usage
```sh
git clone https://github.com/deter0/xborder
cd xborder
chmod +x xborders
./xborders --help
```
### Dependencies
Make sure you have these!
* pycairo (Tested with version 1.21.0, `pip install pycairo`)
* libwnck (Tested with version 40.1-1 `sudo pacman -S libwnck3`)
* gtk
* a compositor ([picom](https://github.com/yshui/picom) is what I am using or you can use another compositor) although even compton with work, just something that supports transparent windows.

### Note for compositor
If you don't want your entire screen blurred please add `role = 'xborder'` to your blur-exclude!
```
blur-background-exclude = [
  # prevents picom from blurring the background
  "role   = 'xborder'",
  ...
];
```

## xborders ontop of i3:
![image](https://user-images.githubusercontent.com/82973108/160370439-8b7a5feb-c186-4954-a029-b718b59fd957.png)
## i3 default:
![image](https://user-images.githubusercontent.com/82973108/160370578-3ea7e3e9-723a-4054-b7b0-2b0110d809c0.png)

### Config
Configuration options can be found by passing in the argument `--help` on the command line, or by specifying a config file with the argument `-c`. The config file is just a simple json file with the keys being the same as the command-line arguments (except without the "--" at the beginning).

# Updating
cd into the xborders directory and run `git pull origin main`
