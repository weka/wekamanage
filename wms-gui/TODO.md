
1. Improve error handling/messages from the 1. code above (add messages to page)
2. Progress bars on install() routines.   
   * Use multiprocessing and readline() to track progress?
   * use st.progess() to display progress bar
3. customize right menu
4. Add configuration of WEKAmon alertmanager
5. Add a postfix or sendmail config so LWH/WEKAmon have a local relay?
6. hosts added to config files - limit the number of hosts listed - large clusters could be a problem.
   1. Maybe randomly pick just a few (3-5?)
   2. ensure they're all backends
7. Enhance log collection with a configuration file that has the log collection commands in it and a framework for "executing" it.
   1. add support for LWH/k8s logs, syslog, and the like
8. Separate SMTP configuration from LWH config - it applies to both WEKAmon and LWH.  Update the config of both tools
9. Perhaps provide start/stop/restart of the subsystems separately from configuring them?
   1. Have a "Save Config" and separate Install/Start/Stop/Restart buttons (as appropriate) on the config pages?
10. audit logging - all commands executed by a shell or UI (cockpit, wms-gui)
11. App state - first login/unconfigured, email configured, cluster configured, LWH configured, etc - a file?
12. SMTP configuration page (applies to LWH and WEKAmon both)
13. Remove SMTP config from LWH page
14. test-resolve all hostnames (SMTP/cluster) when entered and issue appropriate message (add to /etc/hosts?)
15. test connecting to SMTP server


* turn apps.py into an API so it runs outside of streamlit?  This might make container-izing this easier.
FastAPI & uvicorn
https://anderfernandez.com/en/blog/how-to-create-api-python/
pip install fastapi
pip install uvicorn

$ python -m pip install fastapi uvicorn[standard]

