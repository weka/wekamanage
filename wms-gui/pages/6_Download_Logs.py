import datetime
import os
from subprocess import run

import streamlit as st

#from Landing_Page import authenticator
from apps import pushd
from streamlit_common import add_logo, switch_to_login_page

st.set_page_config(page_title="WEKA Management Station Config", page_icon='favicon.ico',
                   layout="wide", menu_items=None)
add_logo("WEKA_Logo_Color_RGB.png")
st.image("WEKA_Logo_Color_RGB.png", width=200)
st.markdown("# WEKA Management Station")

if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = None

if st.session_state["authentication_status"]:
    log = st.session_state.log
    authenticator = st.session_state['authenticator']
    authenticator.logout('Logout', 'sidebar', key="cluster_logout")
    st.title('Download Logs')

    col1, col2, col3 = st.columns(3)

    if st.button('Gather Logs', key='gather_logs'):
        with col1:
            if 'logs_gathered' not in st.session_state:
                # gather the logs
                with st.spinner('Gathering logs and creating support bundle, please wait'):
                    now = datetime.datetime.now()
                    st.session_state['logfile_dir'] = f'/tmp/wms-logs-{now.isoformat()}'
                    os.mkdir(st.session_state.logfile_dir)
                    log.info(f'log dir is {st.session_state.logfile_dir}')
                    st.session_state['logfile_name'] = f'{st.session_state["logfile_dir"]}.tgz'
                    log.info(f'log tarball is {st.session_state.logfile_name}')

                    # gather lwh logs
                    # gather WEKAmon logs
                    with pushd('/opt/weka-mon'):
                        docker_logs = 'docker compose logs -t --until -2m '

                        for service in ['export', 'quota-export', 'grafana', 'prometheus', 'alertmanager', 'loki',
                                        'snaptool']:
                            run(f'{docker_logs} {service} > {st.session_state.logfile_dir}/{service}.log', shell=True)

                        # journalctl -u weka-gui.service > weka_gui.log # collect logs from streamlit service
                        run(f'journalctl -u weka-gui.service > {st.session_state.logfile_dir}/weka_gui.log', shell=True)

                        # tar cvzf {st.session_state.logfile_name} {st.session_state.logfile_dir}
                        with pushd('/tmp'):
                            log.info(f'Creating logfile')
                            subdir = os.path.basename(st.session_state.logfile_dir)  # just makes code clearer
                            run(f'tar cvzf {st.session_state.logfile_name} {subdir}', shell=True)
                        st.session_state['logs_gathered'] = True

    with col1:
        if 'logs_gathered' in st.session_state:
            with open(st.session_state.logfile_name, 'rb') as fp:
                log.info(f'downloading logfile {os.path.basename(st.session_state.logfile_name)}')
                st.download_button("Download Logs", key='download_logs', data=fp,
                                   file_name=os.path.basename(st.session_state.logfile_name),
                                   mime='application/octet-stream')

elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    switch_to_login_page()
