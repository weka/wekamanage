
# WEKA Management Station 1.0.2 Release Notes

#### Scope
This document contains the release notes for WEKA Management Station 1.0.2.  Please visit
https://get.weka.io for the latest updates.

#### Upgrade
Upgrades of existing WMS installations is currently not supported.  Future versions will support in-place upgrades.

## Important Notes
#### **What's New?**

##### V1.0.2
Maintenance release

##### V1.0.1
Maintenance release

##### V1.0.0
Initial Release

##### V1.0.2

This release of WEKA Management Station brings in many improvements and features, expanding the value of your WEKA deployment.

**Tooltips in Web GUI on port 8501**

Most fields in the GUI now include Tooltips - just hover over the ? and you will be provided with a description of the input field.

**Numbered steps in Cluster Deployment Web UI**

The steps to follow in the Cluster Deployment Web UI are now numbered in order to make the UI easier to follow**

**Gathers additional Logs for Diags Download**

The Download Logs function now includes logs from Local Weka Home.

**Updated versions of included Tools**

The WMS includes an updated version of Tools, including enhanced wekachecker and wekconfig.


### Fixed Issues

|  Issue | Details |
|-------------- | -------------- | 
| VT-99 | **The Dell deployment script errors with failed imports**<br>An issue with the venv causes import errors when deploying on the Dell platform<br>_**Configuration:** Deploying new Dell clusters_ | 

|  Issue | Details |
|-------------- | -------------- | 
| VT-100 | **WMS needs `jq` included in OS install**<br>The cluster deployment ui (ansible-install) now requires jq. Now Included with the OS install<br>_**Configuration:** Deploying new clusters_ | 

## Version 1.0.1 Release Content

Updated versions of Local Weka Home and Tools are included in this release.

## Version 1.0.0 Release Content

Initial release


### Known Issues

|  Issue | Details |
|-------------- | -------------- | 
| :red_circle: VT-59 | **eject virtual crdom after install**<br>The kickstart does not explicitly eject the virtual cdrom after installation, which may cause a reboot loop after installation and continuous re-install on certain hypervisors or BMCs._<br>_**Impact:** Never-ending reboot/install cycles_<br>_**Configuration:** Multiple platorms_<br>_**Workaround:** Stop the cycle after the first installation and manually eject the virtual cdrom_ | 

