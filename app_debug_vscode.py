"""Use this module for development with VS Code and the integrated debugger"""
import ptvsd
import streamlit as st

import app

# pylint: disable=invalid-name
markdown = st.markdown(
    """
## Ready to attach the VS Code Debugger!

"""
)


ptvsd.enable_attach(address=("localhost", 5678))
ptvsd.wait_for_attach()

markdown.empty()

app.main()
