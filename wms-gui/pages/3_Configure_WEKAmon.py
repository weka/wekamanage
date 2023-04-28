import requests
import streamlit as st

#from Landing_Page import authenticator
from apps import WEKAmon, NotInstalled, state_text
from streamlit_common import add_logo, switch_to_login_page
from weka_restapi import WekaAPIClient

st.set_page_config(page_title="WEKA Management Station Config", page_icon='favicon.ico',
                   layout="wide", menu_items=None)
# log = logging.getLogger(__name__)
add_logo("WEKA_Logo_Color_RGB.png")
st.image("WEKA_Logo_Color_RGB.png", width=200)
st.markdown("# WEKA Management Station")

if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = None

if st.session_state["authentication_status"]:
    log = st.session_state.log
    authenticator = st.session_state['authenticator']
    authenticator.logout('Logout', 'sidebar', key="cluster_logout")
    st.title('WEKA Cluster Logins')

    # app_config = st.session_state.app_config
    clusterdata = st.session_state.app_config.clusters_config

    # initialize the wekamon app object
    if 'wekamon_app' not in st.session_state:
        try:
            st.session_state['wekamon_app'] = WEKAmon()
        except Exception as exc:
            st.error(exc)
            st.stop()

    app_state = st.session_state.wekamon_app.status()
    st.markdown(f"### WEKAmon Application State:  {state_text(app_state)}")
    st.write()

    col1, col2, col3, col4 = st.columns(4)

    col1, col2 = st.columns(2)
    with col1:
        clusterdata['hostname-ip'] = st.text_input("Cluster Location (hostname or IP addr)", max_chars=30,
                                                   value=clusterdata[
                                                       'hostname-ip'] if 'hostname-ip' in clusterdata else '')
        clusterdata['user'] = st.text_input("Username", max_chars=30,
                                            value=clusterdata['user'] if 'user' in clusterdata else '')
        clusterdata['password'] = st.text_input("Password", max_chars=30, type='password',
                                                value=clusterdata['password'] if 'password' in clusterdata else '')

    if st.button('Save', key='clusters_save'):
        tokens = None
        weka_api = WekaAPIClient(clusterdata['hostname-ip'])
        try:
            tokens = weka_api.login(clusterdata['user'], clusterdata['password'])
        except requests.exceptions.ConnectionError as exc:
            with col1:
                st.error(f'Error connecting to {clusterdata["hostname-ip"]}:\n{exc.args[0]}')
                st.stop()
        except Exception as exc:
            with col1:
                st.error(f'Unexpected error logging into API: {exc.args[0]}')
                st.stop()
        if tokens is not None:
            with col1:
                log.info(f"Successfully logged into WEKA cluster {clusterdata['hostname-ip']}")
                st.success('Login successful')
            st.session_state.app_config.update_tokens(weka_api, tokens)
            st.session_state.app_config.save_clusters()
            # success!
            with col1:
                log.info('Successfully update WEKAmon config files')
                st.success('Successfully updated config files')
            wekamon = st.session_state['wekamon_app']
            if wekamon.status() == NotInstalled:
                with st.spinner("Installing WEKAmon.   Please wait..."):
                    log.info("Installing WEKAmon")
                    wekamon.install()
                    with col1:
                        log.info("WEKAmon successfully installed.")
                        st.success("WEKAmon successfully installed.")
                    wekamon.start()
                    with col1:
                        log.info("WEKAmon successfully started.")
                        st.success("WEKAmon successfully started.")
            else:
                with st.spinner("Restarting WEKAmon.   Please wait..."):
                    log.info("Restarting WEKAmon")
                    wekamon.restart()
                    with col1:
                        log.info("WEKAmon successfully restarted.")
                        st.success("WEKAmon successfully restarted.")

    # update cluster url
    if 'hostname-ip' in clusterdata:
        st.session_state['cluster_url'] = f"http://{clusterdata['hostname-ip']}:14000"


elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    switch_to_login_page()
