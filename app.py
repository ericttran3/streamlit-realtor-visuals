# app.py
import streamlit as st
from src.data_loader import DataLoader
from src.components.overview import render_overview
from src.config import GEO_LEVELS, GEO_MAPPINGS, STATE_TO_FIPS

def main():
    st.set_page_config(
        page_title="Realtor.com Market Insights",
        page_icon="🏠",
        layout="wide",
        menu_items={
            'Get Help': 'mailto:ericttran3@gmail.com',
            'Report a bug': 'mailto:ericttran3@gmail.com',
        }
    )
    
    # Initialize session state
    if 'data_loader' not in st.session_state:
        st.session_state.data_loader = DataLoader()
    
    # Title
    st.title("Realtor.com Market Insights")
    st.markdown("Analyze real estate trends across different geographic levels using data from realtor.com")
    
    # Navigation tabs
    tab_overview, tab_details, tab_compare, tab_map, tab_analyze = st.tabs([
        "Overview", "Details", "Compare", "Map", "Analyze"
    ])
    
    # Overview Tab
    with tab_overview:
        render_overview()
    
    # Details Tab
    with tab_details:
        # render_details()
        st.markdown("""
            <div style='padding: 2rem; background-color: #f8f9fa; border-radius: 0.5rem; text-align: center;'>
                <h3 style='color: #6c757d;'>🚧 Coming Soon! 🚧</h3>
                <p style='color: #6c757d;'>We're working on adding this feature. Stay tuned for updates!</p>
            </div>
        """, unsafe_allow_html=True)

    
    # Compare Tab
    with tab_compare:
        # render_compare()
        st.markdown("""
            <div style='padding: 2rem; background-color: #f8f9fa; border-radius: 0.5rem; text-align: center;'>
                <h3 style='color: #6c757d;'>🚧 Coming Soon! 🚧</h3>
                <p style='color: #6c757d;'>We're working on adding this feature. Stay tuned for updates!</p>
            </div>
        """, unsafe_allow_html=True)        
    
    # Map Tab
    with tab_map:
        # render_map()
        st.markdown("""
            <div style='padding: 2rem; background-color: #f8f9fa; border-radius: 0.5rem; text-align: center;'>
                <h3 style='color: #6c757d;'>🚧 Coming Soon! 🚧</h3>
                <p style='color: #6c757d;'>We're working on adding this feature. Stay tuned for updates!</p>
            </div>
        """, unsafe_allow_html=True)        

# Map Tab
    with tab_analyze:
        # render_analyze()
        st.markdown("""
            <div style='padding: 2rem; background-color: #f8f9fa; border-radius: 0.5rem; text-align: center;'>
                <h3 style='color: #6c757d;'>🚧 Coming Soon! 🚧</h3>
                <p style='color: #6c757d;'>We're working on adding this feature. Stay tuned for updates!</p>
            </div>
        """, unsafe_allow_html=True)                

if __name__ == "__main__":
    main()
