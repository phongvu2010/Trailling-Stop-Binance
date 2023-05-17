import streamlit as st

# Basic Page Configuration
# Find more emoji here: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title = st.secrets['page_title'],
                   page_icon = '📈', layout = 'wide',
                   initial_sidebar_state = 'expanded')

# Inject CSS with Markdown
with open('themes/style.css') as f:
    st.markdown(f'<style>{ f.read() }</style>', unsafe_allow_html = True)
