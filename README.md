# wekamanage
An attempt of a management station for weka

## Building the ISO
1. Clone and Build the Rocky-8.6-LTS repo (https://github.com/weka/Rocky-8.6-LTS)
2. Clone this repo
3. Copy tarballs of local-weka-home, weka-mon, tools, and snaptool to the wekabits/ directory
4. make


## Using the ISO
1. boot a server or vm from the ISO
2. installation is unattended
3. If using a VM, note that you'll need a minimum of 100G disk to install it

## post-installation
1. port 8501 is the wms-gui - default login is admin/admin
2. port 9090 is Cockpit web Linux administration, if you need to change any settings (if not set by DHCP), reviewing logs, etc without having to log into the WMS

### in the wms-gui
1. general workflow is from top to bottom in the left menu
2. when done configuring, you can go back to the landing page and there are buttons to open new tabs for all the applications
