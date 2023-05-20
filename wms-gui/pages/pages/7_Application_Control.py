import streamlit as st
from streamlit_common import add_logo, switch_to_login_page
from apps import WEKAmon, NotInstalled, state_text

menu_items = {
    'get help': 'https://docs.weka.io',
    'About': 'WEKA Management Station v1.0.0  \nwww.weka.io  \nCopyright 2023 WekaIO Inc.  All rights reserved'
}

st.set_page_config(page_title="WMS Services Control", page_icon='favicon.ico',
                   layout="wide", menu_items=menu_items)

if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = None

if st.session_state["authentication_status"]:
    add_logo(st.session_state.logo)
    st.image(st.session_state.logo, width=200)
    st.markdown("# WEKA Management Station")
    log = st.session_state.log
    authenticator = st.session_state['authenticator']
    authenticator.logout('Logout', 'sidebar', key="cluster_logout")
    st.title('WMS Services Control')

    st.session_state.app_config.enable_export = st.checkbox("Enable Metrics Exporter & Grafana",
                                                            value=st.session_state.app_config.enable_export)

    # quota implies quota-export, prometheus, and alertmanager containers, and valid email config
    st.session_state.app_config.enable_quota = st.checkbox("Enable Quota Exporter & Notifications",
                                                           value=st.session_state.app_config.enable_quota)
    # snaptool implies snaptool container
    st.session_state.app_config.enable_snaptool = st.checkbox("Enable Snaptool",
                                                              value=st.session_state.app_config.enable_snaptool)
    # LWH
    st.session_state.app_config.enable_LWH = st.checkbox("Enable Local Weka Home",
                                                              value=st.session_state.app_config.enable_LWH)

    """
    Not Implemented
    
    get status of LWH, WEKAmon, snaptool, etc.
    Show status with checkboxes? Allow user to change checkboxes to up/down services?
    """



elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    switch_to_login_page()