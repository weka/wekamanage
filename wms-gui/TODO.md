
1. Improve error handling/messages from the 1. code above (add messages to page)
2. (done) Fix kickstart in Rocky to %include firewall config, as they differ between wekamanage and weka-software-appliance
3. Progress bars on install() routines.   
   * Use multiprocessing and readline() to track progress?
   * use st.progess() to display progress bar
4. How to run it?   Docker container?   systemd unit? (systemd unit for now - otherwise much vol mapping needed)
5. customize right menu
6. (done) logging instead of print()
7. (done/fixed) page icon (not working?)
8. Add configuration of WEKAmon alertmanager
9. Add a postfix or sendmail config so LWH/WEKAmon have a local relay?


* turn apps.py into an API so it runs outside of streamlit?  This might make container-izing this easier.
FastAPI & uvicorn
https://anderfernandez.com/en/blog/how-to-create-api-python/
pip install fastapi
pip install uvicorn

$ python -m pip install fastapi uvicorn[standard]

