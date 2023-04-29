import requests
import streamlit as st
import yaml

#from Landing_Page import authenticator
from apps import WEKAmon, NotInstalled, state_text
from streamlit_common import add_logo, switch_to_login_page
from weka_restapi import WekaAPIClient

st.set_page_config(page_title="WEKA Management Station Config", page_icon='favicon.ico',
                   layout="wide", menu_items=None)
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
    st.title('Email Notification Settings')

    # app_config = st.session_state.app_config
    clusterdata = st.session_state.app_config.clusters_config

    # initialize the wekamon app object
    if 'email_settings' not in st.session_state:
        try:
            with open(st.session_state.app_config.smtp_config, "r") as f:
                st.session_state['email_settings'] = yaml.safe_load(f)
        except Exception as exc:
            st.error(exc)
            st.stop()

    if 'state' not in st.session_state.email_settings:
        # first time running
        st.session_state.email_settings['state'] = "unconfigured"

    st.write('The settings on this page are for configuring where WMS notification emails will be sent.')
    st.write('Please enter the information below and click Save')
    st.write

    col1, col2, col3, col4 = st.columns(4)

    col1, col2 = st.columns(2)
    with col1:
        smtp_user_data = st.session_state.app_config.smtp_config

        smtp_user_data['sender_email_name'] = st.text_input("Email From Name", max_chars=30,
                                                            value=smtp_user_data['sender_email_name'])
        smtp_user_data['sender_email'] = st.text_input("Email From Address", max_chars=30,
                                                       value=smtp_user_data['sender_email'])
        smtp_user_data['smtp_host'] = st.text_input("Email Relay Host", max_chars=30, #on_change=check_valid_host_ip,
                                                    value=smtp_user_data['smtp_host'])

        smtp_port_no = 25 if smtp_user_data['smtp_port'] == '' else int(smtp_user_data['smtp_port'])

        smtp_port_no = st.number_input("Email Relay Port", step=1, min_value=25, max_value=99999, value=smtp_port_no)

        smtp_user_data['smtp_port'] = str(smtp_port_no)

        smtp_user_data['smtp_username'] = st.text_input("Email Relay Username", max_chars=30,
                                                        on_change=check_valid_user_pass,
                                                        value=smtp_user_data['smtp_username'])
        smtp_user_data['smtp_password'] = st.text_input("Email Relay Password", max_chars=30,
                                                        on_change=check_valid_user_pass,
                                                        value=smtp_user_data['smtp_password'])

        smtp_user_data['smtp_insecure_tls'] = st.checkbox("Allow Insecure TLS with SMTP Relay",
                                                          value=smtp_user_data['smtp_insecure_tls'])

        st.write()

    if st.button('Save', key='email_save'):
        # validate that we can resolve the smtp_host (if not an ip?)
        # validate that we can open a connection to the smtp_host:smtp_port
        # validate that we can log in?
        # can we validate TLS?
        # encrypt password
        # save config file
        # update LWH/WEKAmon/alertmanager configs?   Or add "enable email notifications" buttons to them?


elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    switch_to_login_page()
