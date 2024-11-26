# app.py
import streamlit as st
from src.data_loader import DataLoader
from src.components.overview import render_overview
from src.components.details import render_details
from src.components.compare import render_compare
from src.components.map import render_map
from src.config import GEO_LEVELS, GEO_MAPPINGS, STATE_TO_FIPS

def main():
    st.set_page_config(
        page_title="Realtor.com Market Insights",
        page_icon="🏠",
        # layout="wide"
    )
    
    # Initialize session state
    if 'data_loader' not in st.session_state:
        st.session_state.data_loader = DataLoader()
    
    # Title
    st.title("Realtor.com Market Insights")
    st.markdown("Analyze real estate trends across different geographic levels using data from realtor.com")
    
    # Navigation tabs
    tab_overview, tab_details, tab_compare, tab_map = st.tabs([
        "Overview", "Details", "Compare", "Map"
    ])
    
    # Overview Tab
    with tab_overview:
        render_overview()
    
    # Details Tab
    with tab_details:
        render_details()
    
    # Compare Tab
    with tab_compare:
        render_compare()
    
    # Map Tab
    with tab_map:
        render_map()

if __name__ == "__main__":
    main()
