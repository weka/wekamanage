

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


## Configure Local Weka Home
1. LWH is in /opt/local-weka-home
2. follow directions here (https://docs.weka.io/support/the-wekaio-support-cloud/local-weka-home-deployment), but start from section 4.2

## Configure weka-mon
1. weka-mon is in /opt/weka-mon
2. run the install.sh
3. copy an auth-token.json to /opt/weka-mon/.weka
4. run `docker compose up -d`





