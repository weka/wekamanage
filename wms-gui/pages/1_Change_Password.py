import os

import streamlit as st

from streamlit_common import add_logo, switch_to_login_page

menu_items = {
    'get help': 'https://docs.weka.io',
    'About': 'WEKA Management Station v1.1.1  \nwww.weka.io  \nCopyright 2023 WekaIO Inc.  All rights reserved'
}
st.set_page_config(page_title="WMS Password Change", page_icon='favicon.ico',
                   layout="wide", menu_items=menu_items)
if 'logo' not in st.session_state:
    #st.session_state['logo'] = os.getcwd() + '/WEKA_Logo_Color_RGB.png'
    switch_to_login_page()
add_logo(st.session_state.logo)
st.image(st.session_state.logo, width=200)
st.markdown("# WEKA Management Station")

# st.sidebar.markdown("# Change Password")

if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = None

if st.session_state["authentication_status"]:
    log = st.session_state.log
    authenticator = st.session_state['authenticator']
    authenticator.logout('Logout', 'sidebar', key="change_pw_logout")
    col1, col2, col3 = st.columns(3)
    with col1:
        try:
            if authenticator.reset_password(st.session_state['username'], 'Reset password'):
                st.success('Password modified successfully')
                log.info(f"User {st.session_state.username} changed their password")
        except Exception as e:
            st.error(e)

    # passwd = st.session_state['app_config'].passwords_config

    # passwd = read_passwd_file()
    st.session_state['app_config'].passwords_config['credentials'] = authenticator.credentials
    st.session_state['app_config'].save_passwords()
    # save_passwd_file(passwd)

    # st.write(f'Welcome *{st.session_state["name"]}*')
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    switch_to_login_page()
    # st.warning('Please enter your username and password on the Home page')
