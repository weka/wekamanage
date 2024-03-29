import os

import streamlit as st
import streamlit_monaco_yaml
import yaml

#from Landing_Page import authenticator
from streamlit_common import add_logo, switch_to_login_page, menu_items
from apps import WEKAmon, NotInstalled, state_text

st.set_page_config(page_title="WMS Hardware Monitoring Config", page_icon='favicon.ico',
                   layout="wide", menu_items=menu_items)


if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = None

if st.session_state["authentication_status"]:
    add_logo(st.session_state.logo)
    st.image(st.session_state.logo, width=200)
    st.markdown("# WEKA Management Station")
    log = st.session_state.log
    authenticator = st.session_state['authenticator']
    authenticator.logout('Logout', 'sidebar', key="hw_mon_logout")
    st.title('Hardware Monitoring Configuration')
    st.title('(Only for WekaPOD)')

    hw_mon_config = st.session_state.app_config.hw_mon_config

    if 'hw_mon_initial_text' not in st.session_state:
        st.session_state['hw_mon_initial_text'] = yaml.dump(hw_mon_config)

    st.markdown(f"### Hardware Monitoring Configuration Editor")
    st.write()
    # initialize the wekamon app object
    if 'wekamon_app' not in st.session_state:
        try:
            st.session_state['wekamon_app'] = WEKAmon()
        except Exception as exc:
            st.error(exc)
            st.stop()

    result = streamlit_monaco_yaml.monaco_editor(
        st.session_state.hw_mon_initial_text,
        key=f"monaco_editor",
    )

    # returns None on the initial load
    if result is not None:
        if st.button("Save"):
            st.session_state.app_config.hw_mon_config = yaml.safe_load(result['text'])
            st.session_state.app_config.update_hw_mon()
            st.session_state['hw_mon_initial_text'] = yaml.dump(st.session_state.app_config.hw_mon_config)
            st.success("Hardware Monitor configuration saved")
            if not st.session_state.wekamon_app.is_running('wekasolutions/wekaredfisheventlistener'):
                st.info('Hardware Monitor is not runnning/enabled.  Visit the Configure WEKAmon page to enable it.')

elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    switch_to_login_page()
