import base64

import streamlit as st
from streamlit_javascript import st_javascript

YEAR = '2024'
VERSION = 'v1.2.4'

menu_items = {
    'get help': 'https://docs.weka.io',
    'About': (f'WEKA Management Station {VERSION}  \nwww.weka.io  \nCopyright {YEAR} WekaIO Inc.  All rights reserved')
}

@st.cache_data()
def get_base64_of_bin_file(png_file):
    with open(png_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def build_markup_for_logo(
        png_file,
        background_position="50% 10%",
        margin_top="10%",
        image_width="60%",
        image_height="",
):
    binary_string = get_base64_of_bin_file(png_file)
    return """
            <style>
                [data-testid="stSidebarNav"] {
                    background-image: url("data:image/png;base64,%s");
                    background-repeat: no-repeat;
                    background-position: %s;
                    margin-top: %s;
                    background-size: %s %s;
                }
            </style>
            """ % (
        binary_string,
        background_position,
        margin_top,
        image_width,
        image_height,
    )


def add_logo(png_file):
    if 'logo_markup' not in st.session_state:
        st.session_state['logo_markup'] = build_markup_for_logo(png_file)
    st.markdown(
        st.session_state.logo_markup,
        unsafe_allow_html=True,
    )


def switch_to_login_page():
    switch_page('landing page')


def switch_page(page_name: str):
    from streamlit.runtime.scriptrunner import RerunData, RerunException
    from streamlit.source_util import get_pages

    def standardize_name(name: str) -> str:
        return name.lower().replace("_", " ")

    page_name = standardize_name(page_name)

    pages = get_pages("Landing_Page.py")  # OR whatever your main page is called

    for page_hash, config in pages.items():
        if standardize_name(config["page_name"]) == page_name:
            raise RerunException(
                RerunData(
                    page_script_hash=page_hash,
                    page_name=page_name,
                )
            )

    page_names = [standardize_name(config["page_name"]) for config in pages.values()]

    raise ValueError(f"Could not find page {page_name}. Must be one of {page_names}")


def open_in_new_tab(url):
    js = f'window.open("{url}", "_blank").then(r => window.parent.location.href);'
    st_javascript(js)
    # nav_script = """
    #    <meta http-equiv="refresh" content="0; url='%s'">
    # """ % (url)
    # st.write(nav_script, unsafe_allow_html=True)
