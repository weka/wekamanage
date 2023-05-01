import requests
import streamlit as st

# from Landing_Page import authenticator
from apps import WEKAmon, NotInstalled, state_text
from streamlit_common import add_logo, switch_to_login_page
from weka_restapi import WekaAPIClient

menu_items = {
    'get help': 'https://docs.weka.io',
    'About': 'WEKA Management Station v1.0.0  \nwww.weka.io  \nCopyright 2023 WekaIO Inc.  All rights reserved'
}

st.set_page_config(page_title="WMS Config WEKAmon", page_icon='favicon.ico',
                   layout="wide", menu_items=menu_items)
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
    st.title('WEKAmon Services Configuration')

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
        # export implies export, prometheus, and grafana containers
        st.session_state.app_config.enable_export = st.checkbox("Enable Metrics Exporter & Grafana",
                                                                value=st.session_state.app_config.enable_export)
        if st.session_state.app_config.enable_export:
            st.session_state.app_config.enable_alerts = st.checkbox("Enable Alert Notifications",
                                                                    value=st.session_state.app_config.enable_alerts)
        # quota implies quota-export, prometheus, and alertmanager containers, and valid email config
        st.session_state.app_config.enable_quota = st.checkbox("Enable Quota Exporter & Notifications",
                                                               value=st.session_state.app_config.enable_quota)
        # snaptool implies snaptool container
        st.session_state.app_config.enable_snaptool = st.checkbox("Enable Snaptool",
                                                                  value=st.session_state.app_config.enable_snaptool)
        # loki implies loki container
        st.session_state.app_config.enable_loki = st.checkbox("Enable WEKAmon Log storage",
                                                              value=st.session_state.app_config.enable_loki)

        # if any of the above are True, then we need to authenticate with the cluster
        if st.session_state.app_config.enable_export or \
                st.session_state.app_config.enable_quota or \
                st.session_state.app_config.enable_snaptool or \
                st.session_state.app_config.enable_loki:
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
                    st.error("Make sure you have DNS configured or have edited /etc/hosts")
                    st.error("See the OS Web Admin GUI on the Landing Page to configure DNS")
                    st.error("See the Edit Hosts File page to edit the hosts file")
                    st.stop()
            except Exception as exc:
                with col1:
                    st.error(f'Unexpected error logging into API: {exc.args[0]}')
                    st.stop()
            if tokens is not None:  # was the cluster login successful?
                with col1:
                    log.info(f"Successfully logged into WEKA cluster {clusterdata['hostname-ip']}")
                    st.success('Successfully logged into cluster')
                st.session_state.app_config.update_tokens(weka_api, tokens)

                # so instead of the next line, we'll need to assemble the docker-compose.yml with the
                # services selected, then save the config files for the services selected only.
                st.session_state.app_config.save_clusters()
                st.session_state.app_config.configure_compose()

                # success!
                with col1:
                    log.info('Successfully updated WEKAmon config files')
                    st.success('Successfully updated config files')

                # we may want to put this on another screen or after another button... start/stop services
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

            else:
                # cluster login failed.  disable WEKAmon completely because we don't have valid credentials
                wekamon = st.session_state['wekamon_app']
                wekamon.stop()  # does this prevent start on reboot?

    # update cluster url
    if 'hostname-ip' in clusterdata:
        st.session_state['cluster_url'] = f"http://{clusterdata['hostname-ip']}:14000"



elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    switch_to_login_page()
