import os

import streamlit as st

# from Landing_Page import authenticator
from apps import LocalWekaHome, NotInstalled, MiniKube, state_text
from streamlit_common import add_logo, switch_to_login_page

menu_items = {
    'get help': 'https://docs.weka.io',
    'About': 'WEKA Management Station v1.1.3  \nwww.weka.io  \nCopyright 2023 WekaIO Inc.  All rights reserved'
}

st.set_page_config(page_title="WMS LWH Config", page_icon='favicon.ico',
                   layout="wide", menu_items=menu_items)


def config_lwh():
    log = st.session_state.log

    # def callback_func(*args, **kwargs):
    #    print(f"args is '{args}', kwargs is '{kwargs}'")
    #    st.error("this is an error")

    def check_valid_domain():
        pass

    def check_not_empty():
        if len(st.session_state.email_link) == 0:
            st.error("Entry is Required")
            return False
        else:
            return True
        pass

    log.info('starting LWH configuration')
    if 'app_config' not in st.session_state:
        st.error("app configuration not loaded")
        st.stop()
    elif not st.session_state.app_config.configs_loaded:
        st.error("lwh configuration not loaded")
        st.stop()
    else:
        config = st.session_state.app_config.lwh_config

    # initialize the lwh app object
    if 'lwh_app' not in st.session_state:
        try:
            st.session_state['lwh_app'] = LocalWekaHome()
        except Exception as exc:
            st.error(exc)
            st.stop()

    st.markdown("## Local WEKA Home Configuration")

    app_state = st.session_state.lwh_app.status()
    st.markdown(f"### Local Weka Home Application State:  {state_text(app_state)}")
    st.write()
    st.markdown("### Web Configuration:")

    global_config = config['global']

    col1, col2 = st.columns(2)
    with col1:
        global_config['ingress']['domain'] = st.text_input(
            "Listen Address/Domain",
            max_chars=30, on_change=check_valid_domain,
            value=global_config['ingress']['domain'],
            help="Address/hostname that LWH will listen on.  Leave blank or use 0.0.0.0 to listen on all interfaces," +
            " or an IP address, hostname, or FQDN as may be required by the TLS certificate")

        if config['alertdispatcher']['email_link_domain_name'] is None or \
                len(config['alertdispatcher']['email_link_domain_name']) == 0:
            config['alertdispatcher']['email_link_domain_name'] = st.session_state.domain
        config['alertdispatcher']['email_link_domain_name'] = st.text_input(
            "Email Alert Domain Name: (REQUIRED)",
            help="A domain name (or ip address) to use in Alert Email URL links, for example: " +
                 "sample.com will result in links of https://sample.com/something." +
                 " It is likely the domain you use to access WMS (this server's name)",
            max_chars=30, on_change=check_not_empty,
            key="email_link",
            value=config['alertdispatcher']['email_link_domain_name'])
        st.write()

        st.write()
        st.markdown("### Web Server TLS Cert Configuration:")

        tls = global_config['ingress']['nginx']['tls']
        tls['enabled'] = st.checkbox("Enable Ingress TLS?",
                                     value=tls['enabled'],
                                     help="Should TLS be used for all connections?")
        tls['cert'] = st.text_area("TLS Cert:", value=tls['cert'],
                                   help="The TLS certificate that should be used")
        tls['key'] = st.text_area("TLS Key:", value=tls['key'],
                                  help="The TLS key that matches the certificate above")
        st.write()

        st.markdown("### Email Alert Configuration:")
        st.session_state.app_config.smtp_config['enable_lwh_email'] = \
            st.checkbox("Enable email notifications (configure in the Email Notification Settings page)",
                        help="Please configure email server settings on the Email Notification Settings page",
                        value=st.session_state.app_config.smtp_config['enable_lwh_email'])

        st.markdown("### Forward to Cloud Weka Home:")
        st.session_state.app_config.smtp_config['api_forwarding'] = \
        config['apiforwarding']['enabled'] = \
            st.checkbox("Enable forwarding data to Cloud Weka Home",
                        help="Requires internet connectivity to api.home.weka.io",
                        value=config['apiforwarding']['enabled'])

        if st.button("Save and install/start LWH"):
            # bool from above checkbox
            if st.session_state.app_config.smtp_config['enable_lwh_email']:
                # if the config is not validated, error
                if st.session_state.app_config.smtp_config['validated']:
                    smtp_config = st.session_state.app_config.smtp_config
                    lwh_smtp_user_data = config['smtp_user_data']
                    lwh_smtp_user_data['sender_email'] = smtp_config['sender_email']
                    lwh_smtp_user_data['sender_email_name'] = smtp_config['sender_email_name']
                    lwh_smtp_user_data['smtp_host'] = smtp_config['smtp_host']
                    lwh_smtp_user_data['smtp_port'] = smtp_config['smtp_port']
                    lwh_smtp_user_data['smtp_username'] = smtp_config['smtp_username']
                    lwh_smtp_user_data['smtp_password'] = smtp_config['smtp_password']
                    lwh_smtp_user_data['smtp_insecure_tls'] = smtp_config['smtp_insecure_tls']
                else:
                    st.error("Invalid SMTP configuration - go to Email Notification Settings page to configure")
                    st.session_state.app_config.smtp_config.enable_lwh_email = False
                    # stop, or continue?
                    st.stop()

            st.session_state['app_config'].save_lwh_config()
            st.success('Configuration saved')
            if 'minikube_app' not in st.session_state:
                st.session_state['minikube_app'] = MiniKube()
            if st.session_state.minikube_app.status() == NotInstalled:
                log.info("minikube not installed, attempting installation")
                with st.spinner(
                        'Installing minikube, please wait (this can take several minutes)' +
                        ' Do not navigate away until complete.'):
                    try:
                        st.session_state.minikube_app.install()
                        st.success("Minikube installed")
                    except Exception as exc:
                        st.error(exc)
                        st.stop()
            if 'lwh_app' not in st.session_state:
                st.session_state['lwh_app'] = LocalWekaHome()
            if st.session_state.lwh_app.status() == NotInstalled:
                log.info("lwh not installed, attempting installation")
                with st.spinner('Installing Local Weka Home, please wait (this can take several minutes)' +
                                ' Do not navigate away until complete.'):
                    if not st.session_state.lwh_app.install():
                        log.error('Error installing/updating LWH')
                        st.error('Error installing/updating LWH')
                    else:
                        log.info("Local Weka Home installed")
                        st.success("Local Weka Home installed")
            else:
                with st.spinner('Updating Local Weka Home, please wait (this can take several minutes)'):
                    if not st.session_state.lwh_app.start():
                        log.error('Error starting LWH')
                        st.error('Error starting LWH')

        if st.session_state.lwh_app.status() != NotInstalled:
            if st.button("Get Admin Password"):
                st.write(f"Admin Password is {st.session_state.lwh_app.admin_password()}")
            if st.button("Get Grafana Password"):
                st.write(f"Grafana Password is {st.session_state.lwh_app.grafana_password()}")



if "authentication_status" not in st.session_state or \
        st.session_state["authentication_status"] is None or \
        st.session_state["authentication_status"] is False:
    switch_to_login_page()
elif st.session_state["authentication_status"]:
    authenticator = st.session_state['authenticator']
    authenticator.logout('Logout', 'sidebar', key="lwh_logout")
    #if 'logo' not in st.session_state:
    #    st.session_state['logo'] = os.getcwd() + '/WEKA_Logo_Color_RGB.png'
    add_logo(st.session_state.logo)
    st.image(st.session_state.logo, width=200)
    st.markdown("# WEKA Management Station Configuration")
    config_lwh()
