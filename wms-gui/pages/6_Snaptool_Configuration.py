import streamlit as st
import streamlit_monaco_yaml
import yaml

#from Landing_Page import authenticator
from streamlit_common import add_logo, switch_to_login_page
from apps import WEKAmon, NotInstalled, state_text


menu_items = {
    'get help': 'https://docs.weka.io',
    'About': 'WEKA Management Station v1.0.0  \nwww.weka.io  \nCopyright 2023 WekaIO Inc.  All rights reserved'
}

st.set_page_config(page_title="WMS Snaptool Config", page_icon='favicon.ico',
                   layout="wide", menu_items=menu_items)

add_logo("WEKA_Logo_Color_RGB.png")
st.image("WEKA_Logo_Color_RGB.png", width=200)
st.markdown("# WEKA Management Station")

if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = None

if st.session_state["authentication_status"]:
    log = st.session_state.log
    authenticator = st.session_state['authenticator']
    authenticator.logout('Logout', 'sidebar', key="snaptool_logout")
    st.title('Snaptool Configuration')

    snaptool_config = st.session_state.app_config.snaptool_config

    if 'snaptool_initial_text' not in st.session_state:
        st.session_state['snaptool_initial_text'] = yaml.dump(snaptool_config)

    st.markdown(f"### Snaptool Configuration Editor")
    st.write()
    # initialize the wekamon app object
    if 'wekamon_app' not in st.session_state:
        try:
            st.session_state['wekamon_app'] = WEKAmon()
        except Exception as exc:
            st.error(exc)
            st.stop()

    result = streamlit_monaco_yaml.monaco_editor(
        st.session_state.snaptool_initial_text,
        key=f"monaco_editor",
    )

    # returns None on the initial load
    if result is not None:
        if st.button("Save"):
            st.session_state.app_config.snaptool_config = yaml.safe_load(result['text'])
            st.session_state.app_config.update_snaptool()
            st.session_state['snaptool_initial_text'] = yaml.dump(st.session_state.app_config.snaptool_config)
            st.success("Snaptool configuration saved")
            if not st.session_state.wekamon_app.is_running('wekasolutions/snaptool'):
                st.info('Snaptool is not runnning/enabled.  Visit the Configure WEKAmon page to enable it.')

elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    switch_to_login_page()
