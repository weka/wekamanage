
1. Improve error handling/messages from the 1. code above (add messages to page)
2. Progress bars on install() routines.   
   * Use multiprocessing and readline() to track progress?
   * use st.progess() to display progress bar
3. Add configuration of WEKAmon alertmanager
   1. idea... have templates for each notification type
   2. build the config file on change
4. Add a postfix or sendmail config so LWH/WEKAmon have a local relay?
5. Enhance log collection with a configuration file that has the log collection commands in it and a framework for "executing" it.
   1. add support for LWH/k8s logs, syslog, and the like
6. Separate SMTP configuration from LWH config - it applies to both WEKAmon and LWH.  Update the config of both tools
7. Perhaps provide start/stop/restart of the subsystems separately from configuring them?
   1. Have a "Save Config" and separate Install/Start/Stop/Restart buttons (as appropriate) on the config pages?
8. audit logging - all commands executed by a shell or UI (cockpit, wms-gui)
9. App state - first login/unconfigured, email configured, cluster configured, LWH configured, etc - a file?
10. SMTP configuration page (applies to LWH and WEKAmon both)
11. Remove SMTP config from LWH page
12. test-resolve all hostnames (SMTP/cluster) when entered and issue appropriate message (add to /etc/hosts?)
13. test connecting to SMTP server
14. Docker Compose config file auto-gen
    1. have template files for each container (grafana, prom, loki, export, etc)
    2. Add them to the docker-compose.yml when the services are selected
    3. restart compose


* turn apps.py into an API so it runs outside of streamlit?  This might make container-izing this easier.
FastAPI & uvicorn
https://anderfernandez.com/en/blog/how-to-create-api-python/
pip install fastapi
pip install uvicorn

$ python -m pip install fastapi uvicorn[standard]

