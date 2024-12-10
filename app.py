# app.py
import streamlit as st

# Must be the first Streamlit command
st.set_page_config(
    page_title="Realtor.com Market Insights",
    page_icon="🏠",
    layout="centered",
    menu_items={
        'Get Help': 'mailto:ericttran3@gmail.com',
        'Report a bug': 'mailto:ericttran3@gmail.com',
    }
)

# Apply custom CSS right after set_page_config
with open('src/assets/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Now import other modules
from tools.overview import main as overview_main
from tools.compare import compare_page  # Make sure this matches your compare.py function name
from tools.map import render_map_view as map_main
st.logo("src/assets/buildings.svg")


def placeholder_map():
    st.title("Map")
    st.write("Coming soon...")

def placeholder_chat():
    st.title("Chat")
    st.write("Coming soon...")    

def placeholder_bugs():
    st.title("Bug Reports")
    st.write("Coming soon...")

def placeholder_notifications():
    st.title("Alerts")
    st.write("Coming soon...")

def placeholder_sources():
    st.title("Sources")
    st.write("Coming soon...")

def placeholder_about():
    st.title("About")
    st.write("Coming soon...")

# Create pages with unique titles
overview = st.Page(overview_main, title="Overview", icon=":material/search:", default=True)
compare = st.Page(compare_page, title="Compare", icon=":material/history:")  # Updated to match the function name
map = st.Page(placeholder_map, title="Map", icon=":material/map:")
chat = st.Page(placeholder_chat, title="Chat", icon=":material/chat:")
# map_page = st.Page(map_main, title="Map", icon=":material/map:")

notifications = st.Page(placeholder_notifications, title="Notifications", icon=":material/notification_important:")
bugs = st.Page(placeholder_bugs, title="Bug Reports", icon=":material/bug_report:")
sources = st.Page(placeholder_sources, title="Sources", icon=":material/data_object:")
about = st.Page(placeholder_about, title="About", icon=":material/info:")

# Navigation without login
pg = st.navigation(
    {
        "Tools": [overview, compare, map, chat],
        "Reports": [notifications, bugs],
        "Resources": [sources, about]
    }
)

pg.run()
