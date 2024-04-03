import os

import requests
import streamlit as st

# from Landing_Page import authenticator
from apps import WEKAmon, NotInstalled, state_text
from streamlit_common import add_logo, switch_to_login_page, menu_items
from weka_restapi import WekaAPIClient

st.set_page_config(page_title="WMS Config WEKAmon", page_icon='favicon.ico',
                   layout="wide", menu_items=menu_items)

if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = None

if st.session_state["authentication_status"]:
    # if 'logo' not in st.session_state:
    #    st.session_state['logo'] = os.getcwd() + '/WEKA_Logo_Color_RGB.png'
    add_logo(st.session_state.logo)
    st.image(st.session_state.logo, width=200)
    st.markdown("# WEKA Management Station")
    log = st.session_state.log
    authenticator = st.session_state['authenticator']
    authenticator.logout('Logout', 'sidebar', key="cluster_logout")
    st.title('WEKAmon Services Configuration')

    # app_config = st.session_state.app_config
    st.session_state.app_config.clusters_config = st.session_state.app_config.clusters_config

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
                                                                value=st.session_state.app_config.enable_export,
                                                                help="Enable Grafana performance metrics")
        # if st.session_state.app_config.enable_export:
        #    st.session_state.app_config.enable_alerts = st.checkbox("Enable Alert Notifications",
        #                                                            value=st.session_state.app_config.enable_alerts)

        # quota implies quota-export, prometheus, and alertmanager containers, and valid email config
        st.session_state.app_config.enable_quota = st.checkbox("Enable Quota Exporter & Notifications",
                                                               value=st.session_state.app_config.enable_quota,
                                                               help="Enable WEKA Quota alerting")
        # snaptool implies snaptool container
        st.session_state.app_config.enable_snaptool = st.checkbox("Enable Snaptool",
                                                                  value=st.session_state.app_config.enable_snaptool,
                                                                  help="Enable automatic snapshot scheduling")
        # loki implies loki container
        st.session_state.app_config.enable_loki = st.checkbox("Enable WEKAmon Log storage",
                                                              value=st.session_state.app_config.enable_loki,
                                                              help="Enable long-term Event storage")
        # hw monitoring implies wekaredfisheventlistener container
        st.session_state.app_config.enable_hw_mon = st.checkbox("Enable WEKA Hardware Monitoring",
                                                              value=st.session_state.app_config.enable_hw_mon,
                                                              help="Enable Hardware Monitoring")

        # if any of the above are True, then we need to authenticate with the cluster
        if st.session_state.app_config.enable_export or \
                st.session_state.app_config.enable_quota or \
                st.session_state.app_config.enable_snaptool or \
                st.session_state.app_config.enable_loki or \
                st.session_state.app_config.enable_hw_mon:
            st.session_state.app_config.clusters_config['hostname-ip'] = st.text_input(
                "Cluster Location (hostname or IP addr)", max_chars=50,
                value=st.session_state.app_config.clusters_config[
                    'hostname-ip'] if 'hostname-ip' in st.session_state.app_config.clusters_config else '',
                help="The name or IP of one of your WEKA servers")
            st.session_state.app_config.clusters_config['user'] = \
                st.text_input("Username", max_chars=50,
                              value= st.session_state.app_config.clusters_config[
                                  'user'] if 'user' in st.session_state.app_config.clusters_config else '',
                              help="WEKA username for cluster login")
            st.session_state.app_config.clusters_config['password'] = \
                st.text_input("Password", max_chars=50, type='password',
                              value=st.session_state.app_config.clusters_config[
                                  'password'] if 'password' in st.session_state.app_config.clusters_config else '',
                              help="WEKA password for the WEKA username specified above")

        if st.button('Save and start selected services', key='clusters_save'):
            tokens = None
            print(os.getcwd())
            if 'weka_api' not in st.session_state:
                st.session_state['weka_api'] = WekaAPIClient(st.session_state.app_config.clusters_config['hostname-ip'])
            try:
                tokens = st.session_state.weka_api.login(st.session_state.app_config.clusters_config['user'],
                                                         st.session_state.app_config.clusters_config['password'], timeout=10)
            except requests.exceptions.ConnectionError as exc:
                with col1:
                    st.error(
                        f'Error connecting to {st.session_state.app_config.clusters_config["hostname-ip"]}:\n{exc.args[0]}')
                    st.error("Make sure you have DNS configured or have edited /etc/hosts")
                    st.error("See the OS Web Admin GUI on the Landing Page to configure DNS")
                    st.error("See the Edit Hosts File page to edit the hosts file")
                    del st.session_state['weka_api']
                    st.stop()
            except Exception as exc:
                with col1:
                    st.error(f'Unexpected error logging into API: {exc.args[0]}')
                    del st.session_state['weka_api']
                    st.stop()
            if tokens is not None:  # was the cluster login successful?
                with col1:
                    log.info(
                        f"Successfully logged into WEKA cluster {st.session_state.app_config.clusters_config['hostname-ip']}")
                    st.success('Successfully logged into cluster')
                st.session_state.app_config.update_tokens(st.session_state.weka_api, tokens)

                # so instead of the next line, we'll need to assemble the docker-compose.yml with the
                # services selected, then save the config files for the services selected only.
                # wekamon = st.session_state.wekamon_app
                # status = wekamon.status()
                # if status != NotInstalled:
                #    # stop compose before changing the config file in case we remove something...
                #    wekamon.stop()
                st.session_state.wekamon_app.stop()
                st.session_state.app_config.save_clusters()
                # Generate the compose.yml config file
                st.session_state.app_config.configure_compose()
                st.session_state.app_config.configure_prometheus()
                # if status != NotInstalled:
                #    wekamon.start()
                #st.session_state.wekamon_app.start()

                # success!
                with col1:
                    log.info('Successfully updated WEKAmon config files')
                    st.success('Successfully updated config files')

                # we may want to put this on another screen or after another button... start/stop services
                if st.session_state.wekamon_app.status() == NotInstalled:
                    with st.spinner("Installing WEKAmon.   Please wait..."):
                        log.info("Installing WEKAmon")
                        st.session_state.wekamon_app.install()
                        with col1:
                            log.info("WEKAmon successfully installed.")
                            st.success("WEKAmon successfully installed.")
                        st.session_state.wekamon_app.start()
                        with col1:
                            log.info("WEKAmon successfully started.")
                            st.success("WEKAmon successfully started.")
                else:
                    with st.spinner("Restarting WEKAmon.   Please wait..."):
                        log.info("Restarting WEKAmon")
                        st.session_state.wekamon_app.restart()
                        with col1:
                            log.info("WEKAmon successfully restarted.")
                            st.success("WEKAmon successfully restarted.")

            else:
                # cluster login failed.  disable WEKAmon completely because we don't have valid credentials
                # wekamon = st.session_state['wekamon_app']
                del st.session_state['weka_api']
                st.session_state.wekamon_app.stop()  # does this prevent start on reboot?

    # update cluster url
    if 'hostname-ip' in st.session_state.app_config.clusters_config:
        st.session_state['cluster_url'] = f"http://{st.session_state.app_config.clusters_config['hostname-ip']}:14000"

    # put into a pandas frame?
    # compose_out = st.session_state.wekamon_app.compose_ps()
    # for line in compose_out.split('\n'):
    #    st.write(line)



elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    switch_to_login_page()
