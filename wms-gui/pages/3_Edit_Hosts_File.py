import streamlit as st
import streamlit_monaco_yaml

# from Landing_Page import authenticator
from streamlit_common import add_logo, switch_to_login_page

menu_items = {
    'get help': 'https://docs.weka.io',
    'About': 'WEKA Management Station v1.0.0  \nwww.weka.io  \nCopyright 2023 WekaIO Inc.  All rights reserved'
}

st.set_page_config(page_title="WMS Edit Hosts File", page_icon='favicon.ico',
                   layout="wide", menu_items=menu_items)


if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = None

if st.session_state["authentication_status"]:
    add_logo("WEKA_Logo_Color_RGB.png")
    st.image("WEKA_Logo_Color_RGB.png", width=200)
    st.markdown("# WEKA Management Station")
    log = st.session_state.log
    authenticator = st.session_state['authenticator']
    authenticator.logout('Logout', 'sidebar', key="snaptool_logout")
    st.title('Edit /etc/hosts')

    if 'etc_hosts' not in st.session_state:
        with open('/etc/hosts', 'r') as f:
            st.session_state['etc_hosts'] = f.read()

    st.markdown(f"### /etc/hosts File Editor")
    st.write()

    result = streamlit_monaco_yaml.monaco_editor(
        st.session_state.etc_hosts,
        # schema=json_schema,
        # height=1000,
        # a unique key avoids to reload the editor each time the content changed
        key=f"monaco_editor",
    )

    # returns None on the initial load
    if result is not None:
        # print(yaml.safe_load(result['text']))

        if st.button("Save"):
            log.info("Saving /etc/hosts file")
            st.session_state.etc_hosts = result['text']
            with open('/etc/hosts', 'w') as f:
                f.write(st.session_state.etc_hosts)
                log.info("/etc/hosts file Saved")
                st.success("/etc/hosts file Saved")

elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    switch_to_login_page()
