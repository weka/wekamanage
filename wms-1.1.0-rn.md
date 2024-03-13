
# WEKA Management Station 1.0.2 Release Notes

#### Scope
This document contains the release notes for WEKA Management Station 1.0.2.  Please visit
https://get.weka.io for the latest updates.

#### Upgrade
Upgrades of existing WMS installations is currently not supported.  Future versions will support in-place upgrades.

## Important Notes
#### **What's New?**

##### V1.1.0
Maintenance release

##### V1.0.2
Maintenance release

##### V1.0.1
Maintenance release

##### V1.0.0
Initial Release


## Version 1.1.0 Release Content

This release of WEKA Management Station brings in many improvements and features, expanding the value of your WEKA deployment.

**Updated versions of included Tools**

The WMS includes an updated version of Tools, including enhanced wekachecker and wekconfig.

**Updated versions of included Utilities**

The WMS includes an updated version of LWH and WEKAmon

### Fixed Issues


| Issue | Details                                                                                                                                                      |
|-------|--------------------------------------------------------------------------------------------------------------------------------------------------------------| 
| VT-89 | **Add GUI to disable LWH uploads**<br>LWH now automatically uploads to CWH, and this checkbox disables this feature<br>**Configuration:** All configurations | 

| Issue | Details                                                                                                                                                                       |
|-------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| 
| VT-96 | **Correct mis-stated minimum disk requirements**<br>Docs were incorrect stating minimum disk requirements for the management station<br>**Configuration:** All configurations | 

| Issue  | Details                                                                                                                                                                      |
|--------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| 
| VT-108 | **Grey out buttons for services not running**<br>Landing Page buttons for services not configured are greyed out to prevent failing<br>**Configuration:** All configurations | 

| Issue  | Details                                                                                                      |
|--------|--------------------------------------------------------------------------------------------------------------| 
| VT-119 | **Timezone set to EST**<br>Timezone correctly set to UTC by default<br>**Configuration:** All configurations | 

| Issue  | Details                                                                                                                                                    |
|--------|------------------------------------------------------------------------------------------------------------------------------------------------------------| 
| VT-140 | **Sort Landing Page items sensibly**<br>Landing Page sorted with topmost items being the most commonly used items<br>**Configuration:** All configurations | 

| Issue  | Details                                                                                                                                                                                     |
|--------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| 
| VT-122 | **Dynamically generate Prometheus config**<br>Rather than use a static config for Prom, generate one on-the-fly to prevent unnecessary DNS queries<br>**Configuration:** All configurations | 

| Issue | Details                                                                                                                                                                                   |
|-------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| 
| VT-59 | **Install does not eject CDROM after install**<br>Not explicitly ejecting CDROM after install can cause some platforms to get into a reboot loop<br>**Configuration:** All configurations | 

| Issue  | Details                                                                                                                                                 |
|--------|---------------------------------------------------------------------------------------------------------------------------------------------------------| 
| VT-155 | **WEKAmon configuration fields are too narrow**<br>Widened fields so long hostnames and whatnot can be entered<br>**Configuration:** All configurations | 

| Issue  | Details                                                                                                                                                                       |
|--------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| 
| VT-123 | **Grafana tries to use internet**<br>By default, Grafana attempts to check for new versions and report usage.  This is now disabled.<br>**Configuration:** All configurations | 

| Issue  | Details                                                                                                                                                                                                                   |
|--------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| 
| VT-162 | **Grafana displays default dashboard on startup**<br>By default, Grafana displays a default Dashboard.  This is now set to the WEKA Cluster Overview Dashboard for convienience.<br>**Configuration:** All configurations | 

## Version 1.0.2 Release Content

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

| Issue | Details                                                                                                                                                                                          |
|-------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| 
| VT-99 | **The Dell deployment script errors with failed imports**<br>An issue with the venv causes import errors when deploying on the Dell platform<br>_**Configuration:** Deploying new Dell clusters_ | 

| Issue  | Details                                                                                                                                                                                   |
|--------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| 
| VT-100 | **WMS needs `jq` included in OS install**<br>The cluster deployment ui (ansible-install) now requires jq. Now Included with the OS install<br>_**Configuration:** Deploying new clusters_ | 

## Version 1.0.1 Release Content

Updated versions of Local Weka Home and Tools are included in this release.

## Version 1.0.0 Release Content

Initial release


### Known Issues
