import os
import smtplib
import socket
import ssl

import requests
import streamlit as st
import yaml

from apps import WEKAmon, NotInstalled, state_text
from streamlit_common import add_logo, switch_to_login_page
from weka_restapi import WekaAPIClient

menu_items = {
    'get help': 'https://docs.weka.io',
    'About': 'WEKA Management Station v1.0.0\nwww.weka.io'
}
st.set_page_config(page_title="WMS Email Configuration", page_icon='favicon.ico',
                   layout="wide", menu_items=menu_items)
# log = logging.getLogger(__name__)

if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = None

if st.session_state["authentication_status"]:
    #if 'logo' not in st.session_state:
    #    st.session_state['logo'] = os.getcwd() + '/WEKA_Logo_Color_RGB.png'
    add_logo(st.session_state.logo)
    st.image(st.session_state.logo, width=200)

    st.markdown("# WEKA Management Station")
    log = st.session_state.log
    authenticator = st.session_state['authenticator']
    authenticator.logout('Logout', 'sidebar', key="cluster_logout")
    st.title('Email Notification Settings')

    # app_config = st.session_state.app_config
    clusterdata = st.session_state.app_config.clusters_config

    # if 'email_settings' not in st.session_state:
    #    try:
    #        with open(st.session_state.app_config.smtp_config, "r") as f:
    #            st.session_state['email_settings'] = yaml.safe_load(f)
    #    except Exception as exc:
    #        st.error(exc)
    #        st.stop()

    # if 'state' not in st.session_state.email_settings:
    #    # first time running
    #    st.session_state.email_settings['state'] = "unconfigured"

    st.write('The settings on this page are for configuring where/how WMS notification emails will be sent.')
    st.write('Please enter the information below and click Save')
    st.write()

    col1, col2, col3, col4 = st.columns(4)

    col1, col2 = st.columns(2)
    with col1:
        smtp_user_data = st.session_state.app_config.smtp_config

        smtp_user_data['sender_email_name'] = st.text_input("Email From Name", max_chars=50,
                                                            value=smtp_user_data['sender_email_name'])
        smtp_user_data['sender_email'] = st.text_input("Email From Address", max_chars=50,
                                                       value=smtp_user_data['sender_email'])
        smtp_user_data['smtp_host'] = st.text_input("Email Relay Host", max_chars=50,  # on_change=check_valid_host_ip,
                                                    value=smtp_user_data['smtp_host'])

        smtp_port_no = 25 if smtp_user_data['smtp_port'] == '' else int(smtp_user_data['smtp_port'])

        smtp_port_no = st.number_input("Email Relay Port", step=1, min_value=25, max_value=99999, value=smtp_port_no)

        smtp_user_data['smtp_port'] = str(smtp_port_no)

        smtp_user_data['smtp_tls'] = st.checkbox("SMTP Relay allows/requires TLS",
                                                          value=smtp_user_data['smtp_tls'])
        smtp_user_data['smtp_username'] = st.text_input("Email Relay Username", max_chars=50,
                                                        # on_change=check_valid_user_pass,
                                                        value=smtp_user_data['smtp_username'])
        smtp_user_data['smtp_password'] = st.text_input("Email Relay Password", max_chars=50,
                                                        type='password',
                                                        value=smtp_user_data['smtp_password'])

        if smtp_user_data['smtp_tls']:
            smtp_user_data['smtp_insecure_tls'] = st.checkbox("Allow Insecure TLS with SMTP Relay",
                                                              value=smtp_user_data['smtp_insecure_tls'])

        st.write()

    if st.button('Save', key='email_save'):
        # validate that we can resolve the smtp_host (if not an ip?)
        # try:
        #    socket.gethostbyname(smtp_user_data['smtp_host'])
        # except socket.gaierror as e:
        #    st.error(f'Invalid smtp hostname: {e}')
        #    st.info(f'Enter a valid hostname, configure DNS, or edit /etc/hosts (see menu on left)')
        #    st.stop()
        # validate that we can open a connection to the smtp_host:smtp_port
        context = ssl.create_default_context()
        if smtp_user_data['smtp_insecure_tls']:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            # note - default is to verify certs, so we do nothing if smtp_insecure_tls is False
        with col1:
            st.info("Validating configuration")
            try:
                if smtp_user_data['smtp_tls']:
                    server = smtplib.SMTP_SSL(host=smtp_user_data['smtp_host'], port=int(smtp_user_data['smtp_port']),
                                              timeout=5, context=context)
                else:
                    server = smtplib.SMTP(host=smtp_user_data['smtp_host'], port=int(smtp_user_data['smtp_port']),
                                              timeout=5)

                with server:
                    server.ehlo('WMS')
                    if len(smtp_user_data['smtp_username']) != 0:
                        server.login(smtp_user_data['smtp_username'], smtp_user_data['smtp_password'])
            except socket.gaierror as exc:
                st.error(f'Received error connecting to {smtp_user_data["smtp_host"]}: {exc.strerror}')
                st.error("Please verify the Email Relay Host is correct and verify DNS or /etc/hosts settings.")
                st.info("DNS can be set via OS Web Management UI (link on Landing Page)")
                st.info("/etc/hosts can edited on the Edit Hosts File page (on the left menu)")
                if exc.args[0] != -2:
                    st.info(f'Received code {exc.args[0]}')
                st.stop()
            except ssl.SSLEOFError as exc:
                st.error('Host resolved, but could not establish SMTP communications')
                st.info("Please verify Email Relay Host and Port and try again")
                st.stop()
            except ssl.SSLError as exc:
                if exc.args[0] == 1:
                    st.error("SSL Error: did you specify the correct port?")
                    # should probably try non-ssl...
                    st.stop()
            except TimeoutError as exc:
                st.error(f'Timed out connecting to {smtp_user_data["smtp_host"]}')
                st.stop()
            except smtplib.SMTPAuthenticationError as exc:
                st.error(f'Auth Error connecting to {smtp_user_data["smtp_host"]}: {str(exc.args[1])}')
                st.stop()
            except Exception as exc:

                st.error(f'Error connecting to {smtp_user_data["smtp_host"]}: {exc}')
                st.stop()
            st.info("Settings validated")
            # encrypt password?   How can we do this securely when the py code/key is on the system?
            smtp_user_data['validated'] = True
            # save config file
            st.session_state.app_config.save_smtp()
            st.success("Configuration saved.")
            # update LWH/WEKAmon/alertmanager configs?   Or add "enable email notifications" buttons to them?


elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    switch_to_login_page()
