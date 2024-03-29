import os
from logging.handlers import SysLogHandler

import streamlit as st
import streamlit_authenticator as stauth
from streamlit import logger
from streamlit_javascript import st_javascript

from apps import Running, LocalWekaHome, WEKAmon
from streamlit_common import add_logo, open_in_new_tab, menu_items
from app_config import AppConfig

if 'authentication_status' not in st.session_state or not st.session_state['authentication_status']:
    sidebar_state = st.session_state["sidebar_state"] = 'collapsed'
else:
    sidebar_state = st.session_state["sidebar_state"] = 'expanded'

st.set_page_config(page_title="WEKA Management Station Config", page_icon='favicon.ico',
                   layout="wide", initial_sidebar_state=sidebar_state, menu_items=menu_items)

if "log" not in st.session_state:
    log = logger.get_logger('root')
    log.addHandler(SysLogHandler('/dev/log'))
    st.session_state['log'] = log
else:
    log = st.session_state.log

if 'wms_gui_dir' not in st.session_state:
    st.session_state['wms_gui_dir'] = os.getcwd()

if 'app_config' not in st.session_state:
    st.session_state['app_config'] = AppConfig(st.session_state.wms_gui_dir + '/app_config.yml')
    try:
        st.session_state['app_config'].load_configs()
    except Exception as exc:
        log.error(f"Error reading config files: {exc}")
        st.error(f"Error reading config files: {exc}")
        st.stop()

if 'authenticator' not in st.session_state:
    config = st.session_state['app_config'].passwords_config
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )
    st.session_state['authenticator'] = authenticator
else:
    authenticator = st.session_state['authenticator']

    # Get the URL used to get to this app
    # do this twice - it usually fails the first time. (actually, now it works?)
    # do it again after login
    #if "wms_url" not in st.session_state:
    #    url = st_javascript("await fetch('').then(r => window.parent.location.href)")
    #    if type(url) is not int:
    #        st.session_state['wms_url'] = url
            # print(f'got it FIRST time! {url}')

    # actually get their user/pass

if 'logo' not in st.session_state:
    st.session_state['logo'] = os.getcwd() + '/WEKA_Logo_Color_RGB.png'
add_logo(st.session_state['logo'])
st.image(st.session_state.logo, width=200)
st.markdown("# WEKA Management Station")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("## Applications")
    if 'authentication_status' not in st.session_state or not st.session_state['authentication_status']:
        authenticator.login()
        if st.session_state.username is not None and len(st.session_state.username) != 0:
            log.info(f"User {st.session_state.username} logged in")

        # save state - don't need to as authenticator sets these
        # st.session_state['name'] = name
        # st.session_state['authentication_status'] = authentication_status
        # st.session_state['username'] = username

if st.session_state.authentication_status:
    authenticator.logout('Logout', 'sidebar')
    if st.session_state.sidebar_state == 'collapsed':
        st.session_state.sidebar_state = "expanded"
        st.rerun()

    try:
        if st.session_state.lwh_app.status() != Running:
            st.session_state['lwh_up'] = False
        else:
            st.session_state['lwh_up'] = True
        if st.session_state.wekamon_app.status() != Running:
            st.session_state['wekamon_up'] = False
        else:
            st.session_state['wekamon_up'] = True
    except:
        pass  # sometimes on initial load, this pukes with a timeout...

    # Get the URL used to get to this app
    # second time around - usually works like a charm
    if "wms_url" not in st.session_state:
        url = st_javascript("await fetch('').then(r => window.parent.location.href)")
        if type(url) is not int:
            st.session_state['wms_url'] = url
            log.error('second try succeeded')

    if "wms_url" in st.session_state:
        # print(st.session_state['wms_url'])
        # figure out the URLs to LWH, WEKAmon, and Snaptool
        our_ip = st.session_state.wms_url.split(':')[1]  # should be 3; 'http', '//<hostname/ip>' and port #
        HTTP='http://'
        HTTPS='https://'
        if "lwh_url" not in st.session_state:
            tempvar1 = st.session_state.wms_url.split(':')  # should be 3; 'http', '//<hostname/ip>' and port #
            st.session_state['lwh_url'] = f"{tempvar1[0]}:{tempvar1[1]}"  # leave off port: should be port 80 by default
            # st.markdown(f'<a href="{st.session_state.lwh_url}" target="_self">Open Local WEKA Home </a>', unsafe_allow_html=True)

        if "domain" not in st.session_state:
            st.session_state['domain'] = st.session_state['lwh_url'][7:]

        if "grafana_url" not in st.session_state:
            st.session_state['grafana_url'] = st.session_state['lwh_url'] + ":3000"
            st.session_state['prometheus_url'] = st.session_state['lwh_url'] + ":9091"
            st.session_state['alertmanager_url'] = st.session_state['lwh_url'] + ":9093"

        if "snaptool_url" not in st.session_state:
            st.session_state['snaptool_url'] = st.session_state['lwh_url'] + ":8090"

        if 'app_config' in st.session_state and 'cluster_url' not in st.session_state:
            clusterip = st.session_state.app_config.clusters_config['hostname-ip']
            if clusterip is not None and len(clusterip) > 0:
                st.session_state['cluster_url'] = f'https://{clusterip}:14000'

        if "cockpit_url" not in st.session_state:
            st.session_state['cockpit_url'] = st.session_state['lwh_url'] + ":9090"

        if "ansible_url" not in st.session_state:
            st.session_state['ansible_url'] = st.session_state['lwh_url'] + ":7860"

        with col1:
            st.markdown('### Applications')

            st.write('WEKAmon')
            if st.button("Grafana", disabled='wekamon_up' not in st.session_state or not st.session_state['wekamon_up']):
                log.info(f'opening {st.session_state.grafana_url}')
                open_in_new_tab(st.session_state.grafana_url)

            st.write('Local Weka Home')
            if st.button("Local WEKA Home", disabled='lwh_up' not in st.session_state or not st.session_state['lwh_up']):
                log.info(f'opening {st.session_state.lwh_url}')
                open_in_new_tab(st.session_state.lwh_url)

            st.write('Snaptool')
            if st.button("Snaptool", disabled='wekamon_up' not in st.session_state or not st.session_state['wekamon_up']):
                log.info(f'opening {st.session_state.snaptool_url}')
                open_in_new_tab(st.session_state.snaptool_url)

            st.write('WMS OS management')
            if st.button("WMS Linux Admin GUI"):
                log.info(f'opening {st.session_state.cockpit_url}')
                open_in_new_tab(st.session_state.cockpit_url)

            st.write('Misc')
            if st.button("Prometheus", disabled='wekamon_up' not in st.session_state or not st.session_state['wekamon_up']):
                log.info(f'opening {st.session_state.prometheus_url}')
                open_in_new_tab(st.session_state.prometheus_url)

            if st.button("Alertmanager", disabled='wekamon_up' not in st.session_state or not st.session_state['wekamon_up']):
                log.info(f'opening {st.session_state.alertmanager_url}')
                open_in_new_tab(st.session_state.alertmanager_url)

            st.write('Deploy WEKA Clusters')
            if st.button("Deploy a WEKA Cluster"):
                log.info(f'opening {st.session_state.ansible_url}')
                open_in_new_tab(st.session_state.ansible_url)

            st.write('Manage your WEKA Cluster')
            if st.button("Open cluster GUI", disabled="cluster_url" not in st.session_state):
                log.info(f"opening {st.session_state.cluster_url}")
                open_in_new_tab(st.session_state.cluster_url)

        with col2:
            # initialize the lwh app object
            if 'lwh_app' not in st.session_state:
                try:
                    st.session_state['lwh_app'] = LocalWekaHome()
                except Exception as exc:
                    st.error(exc)
                    st.stop()
            # initialize the wekamon app object
            if 'wekamon_app' not in st.session_state:
                try:
                    st.session_state['wekamon_app'] = WEKAmon()
                except Exception as exc:
                    st.error(exc)
                    st.stop()
            st.markdown("## Application Status")
            st.write()
            try:
                if 'lwh_up' not in st.session_state or st.session_state['lwh_up'] == False:
                    lwh_emoji = ':thumbsdown:'
                else:
                    lwh_emoji = ':thumbsup:'
                if 'wekamon_up' not in st.session_state or st.session_state['wekamon_up'] == False:
                    wekamon_emoji = ':thumbsdown:'
                else:
                    wekamon_emoji = ':thumbsup:'
                st.markdown(f"### Local Weka Home:  {lwh_emoji}")
                st.markdown(f"### WEKAmon:  {wekamon_emoji}")
            except:
                pass    # sometimes on initial load, this pukes with a timeout...


elif st.session_state.authentication_status is False:
    st.error('Username/password is incorrect')
elif st.session_state.authentication_status is None:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.warning('Please enter your username and password')
