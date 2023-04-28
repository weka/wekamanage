import streamlit as st

#from Landing_Page import authenticator
from apps import LocalWekaHome, NotInstalled, MiniKube, state_text
from streamlit_common import add_logo, switch_to_login_page

# log = logging.getLogger(__name__)
st.set_page_config(page_title="WEKA Management Station Config", page_icon='favicon.ico',
                   layout="wide", menu_items=None)


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

    def check_valid_email():
        pass

    def check_valid_host_ip():
        pass

    def check_valid_user_pass():
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
            "Address/Domain that LWH will listen on.  Use 0.0.0.0 or leave blank to listen on all" +
            " interfaces, an FDQN, or hostname",
            max_chars=30, on_change=check_valid_domain,
            value=global_config['ingress']['domain'])

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
            value=config['alertdispatcher'][
                'email_link_domain_name'])
        st.write()
        st.markdown("### Email Alert Configuration:")

        smtp_user_data = config['smtp_user_data']

        smtp_user_data['sender_email_name'] = st.text_input("Email From Name", max_chars=30,
                                                            value=smtp_user_data['sender_email_name'])
        smtp_user_data['sender_email'] = st.text_input("Email From Address", max_chars=30,
                                                       value=smtp_user_data['sender_email'])
        smtp_user_data['smtp_host'] = st.text_input("Email Relay Host", max_chars=30, on_change=check_valid_host_ip,
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
        st.markdown("### Web Server TLS Cert Configuration:")

        tls = global_config['ingress']['nginx']['tls']
        tls['enabled'] = st.checkbox("Enable Ingress TLS?",
                                     value=tls['enabled'])
        tls['cert'] = st.text_area("TLS Cert:", value=tls['cert'])
        tls['key'] = st.text_area("TLS Key:", value=tls['key'])

        if st.button("Save"):
            st.session_state['app_config'].save_lwh_config()
            st.success('Configuration saved')
            if 'minikube_app' not in st.session_state:
                st.session_state['minikube_app'] = MiniKube()
            if st.session_state.minikube_app.status() == NotInstalled:
                log.info("minikube not installed, attempting installation")
                with st.spinner('Installing minikube, please wait (this can take several minutes)'):
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
                with st.spinner('Installing Local Weka Home, please wait (this can take several minutes)'):
                    if not st.session_state.lwh_app.install():
                        log.error('Error installing/updating LWH')
                        st.error('Error installing/updating LWH')
                    else:
                        log.info("Local Weka Home installed")
                        st.success("Local Weka Home installed")
            else:
                with st.spinner('Updating Local Weka Home, please wait (this can take several minutes'):
                    if not st.session_state.lwh_app.start():
                        log.error('Error starting LWH')
                        st.error('Error starting LWH')

        if st.session_state.lwh_app.status() != NotInstalled:
            if st.button("Get Admin Password"):
                st.write(f"Admin Password is {st.session_state.lwh_app.admin_password()}")
            if st.button("Get Grafana Password"):
                st.write(f"Grafana Password is {st.session_state.lwh_app.grafana_password()}")


add_logo("WEKA_Logo_Color_RGB.png")
st.image("WEKA_Logo_Color_RGB.png", width=200)
st.markdown("# WEKA Management Station Configuration")

if "authentication_status" not in st.session_state or \
        st.session_state["authentication_status"] is None or \
        st.session_state["authentication_status"] is False:
    switch_to_login_page()
elif st.session_state["authentication_status"]:
    authenticator = st.session_state['authenticator']
    authenticator.logout('Logout', 'sidebar', key="lwh_logout")
    config_lwh()
