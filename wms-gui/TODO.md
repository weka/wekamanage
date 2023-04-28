
1. Improve error handling/messages from the 1. code above (add messages to page)
2. (done) Fix kickstart in Rocky to %include firewall config, as they differ between wekamanage and weka-software-appliance
3. Progress bars on install() routines.   
   * Use multiprocessing and readline() to track progress?
   * use st.progess() to display progress bar
4. (done) How to run it?   Docker container?   systemd unit? (systemd unit for now - otherwise much vol mapping needed)
5. customize right menu
6. (done) logging instead of print()
7. (done/fixed) page icon (not working?)
8. Add configuration of WEKAmon alertmanager
9. Add a postfix or sendmail config so LWH/WEKAmon have a local relay?
10. hosts added to config files - limit the number of hosts listed - large clusters could be a problem.
    1. Maybe randomly pick just a few (3-5?)
    2. ensure they're all backends
11. Enhance log collection with a configuration file that has the log collection commands in it and a framework for "executing" it.
    1. add support for LWH/k8s logs, syslog, and the like


* turn apps.py into an API so it runs outside of streamlit?  This might make container-izing this easier.
FastAPI & uvicorn
https://anderfernandez.com/en/blog/how-to-create-api-python/
pip install fastapi
pip install uvicorn

$ python -m pip install fastapi uvicorn[standard]

