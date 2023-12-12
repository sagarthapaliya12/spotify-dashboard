import streamlit as st
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="Spotify Dashboard",
        page_icon="👋",
    )

    st.write("# Welcome to Spotify Dashboard! 👋")

    st.sidebar.success("dynamic dashboard options")

    st.markdown(
        """
        You will see the dashboard below
    """
    )


if __name__ == "__main__":
    run()
