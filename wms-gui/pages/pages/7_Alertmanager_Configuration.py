import streamlit as st
import streamlit_monaco_yaml
import yaml

#from Landing_Page import authenticator
from streamlit_common import add_logo, switch_to_login_page
from apps import WEKAmon, NotInstalled, state_text


menu_items = {
    'get help': 'https://docs.weka.io',
    'About': 'WEKA Management Station v1.0.2  \nwww.weka.io  \nCopyright 2023 WekaIO Inc.  All rights reserved'
}

st.set_page_config(page_title="WMS Alertmanager Config", page_icon='favicon.ico',
                   layout="wide", menu_items=menu_items)


if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = None

if st.session_state["authentication_status"]:
    add_logo("WEKA_Logo_Color_RGB.png")
    st.image("WEKA_Logo_Color_RGB.png", width=200)
    st.markdown("# WEKA Management Station")
    log = st.session_state.log
    authenticator = st.session_state['authenticator']
    authenticator.logout('Logout', 'sidebar', key="alertmanager_logout")
    st.title('Alertmanager Configuration')

    alertmanager_config = st.session_state.app_config.alertmanager_config

    if 'alertmanager_initial_text' not in st.session_state:
        st.session_state['alertmanager_initial_text'] = yaml.dump(alertmanager_config)

    st.markdown(f"### Alertmanager Configuration Editor")
    st.write()
    # initialize the wekamon app object
    if 'wekamon_app' not in st.session_state:
        try:
            st.session_state['wekamon_app'] = WEKAmon()
        except Exception as exc:
            st.error(exc)
            st.stop()

    result = streamlit_monaco_yaml.monaco_editor(
        st.session_state.alertmanager_initial_text,
        key=f"alertmanager_monaco_editor",
    )

    # returns None on the initial load
    if result is not None:
        if st.button("Save"):
            st.session_state.app_config.alertmanager_config = yaml.safe_load(result['text'])
            st.session_state.app_config.update_alertmanager()
            st.session_state['alertmanager_initial_text'] = yaml.dump(st.session_state.app_config.alertmanager_config)
            st.success("Alertmanager configuration saved")
            if not st.session_state.wekamon_app.is_running('prom/alertmanager'):
                st.info('Alertmanager is not runnning/enabled.  Visit the Configure WEKAmon page to enable it.')

elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    switch_to_login_page()
