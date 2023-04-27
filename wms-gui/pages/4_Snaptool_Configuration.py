import streamlit as st
import streamlit_monaco_yaml
import yaml

#from Landing_Page import authenticator
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
    authenticator.logout('Logout', 'sidebar', key="snaptool_logout")
    st.title('Snaptool Configuration')

    snaptool_config = st.session_state.app_config.snaptool_config

    if 'initial_text' not in st.session_state:
        st.session_state['initial_text'] = yaml.dump(snaptool_config)

    st.markdown(f"### Snaptool Configuration Editor")
    st.write()

    result = streamlit_monaco_yaml.monaco_editor(
        st.session_state.initial_text,
        # schema=json_schema,
        # height=1000,
        # a unique key avoids to reload the editor each time the content changed
        key=f"monaco_editor",
    )

    # returns None on the initial load
    if result is not None:
        # print(yaml.safe_load(result['text']))

        if st.button("Save"):
            st.session_state.app_config.snaptool_config = yaml.safe_load(result['text'])
            st.session_state.app_config.update_snaptool()
            st.session_state['initial_text'] = yaml.dump(st.session_state.app_config.snaptool_config)

elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    switch_to_login_page()
