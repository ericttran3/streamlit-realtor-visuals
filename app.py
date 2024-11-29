# app.py
import streamlit as st
import streamlit_shadcn_ui as ui
from src.data_loader import DataLoader
from src.components.overview import render_overview, render_support
from src.components.details import render_details
from src.config import GEO_LEVELS, GEO_MAPPINGS, STATE_TO_FIPS

def main():
    st.set_page_config(
        page_title="Realtor.com Market Insights",
        page_icon="🏠",
        layout="centered",
        menu_items={
            'Get Help': 'mailto:ericttran3@gmail.com',
            'Report a bug': 'mailto:ericttran3@gmail.com',
        }
    )
    
    # Add custom CSS for content width
    st.markdown("""
        <style>
            .block-container {
                max-width: 1000px;
                padding-top: 2rem;
                padding-bottom: 2rem;
                padding-left: 2rem;
                padding-right: 2rem;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'data_loader' not in st.session_state:
        st.session_state.data_loader = DataLoader()
    
    # Title
    st.subheader("Realtor.com Market Insights")
    # st.markdown("""
    #     Analyze real estate trends across different geographic levels using weekly and monthly data from <a href="https://realtor.com/research/data" target="_blank" class="title-link">realtor.com</a>
    # """, unsafe_allow_html=True)

    # ui.badges(badge_list=[("shadcn", "default"), ("in", "secondary"), ("streamlit", "destructive")], class_name="flex gap-2", key="main_badges1")
    st.caption("Analyze real estate trends across different geographic levels using weekly and monthly data from realtor.com!")
    
    # Navigation tabs
    tab_overview, tab_details, tab_compare, tab_map, tab_analyze, tab_support = st.tabs([
        "Overview", "Details", "Compare", "Map", "Analyze", "Support"
    ])
    
    # Overview Tab
    with tab_overview:
        render_overview()
    
    # Details Tab
    with tab_details:
        render_details()

    
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

    # Support Tab
    with tab_support:
        # render_support()
        st.markdown("""
            <div style='padding: 2rem; background-color: #f8f9fa; border-radius: 0.5rem; text-align: center;'>
                <h3 style='color: #6c757d;'>🚧 Coming Soon! 🚧</h3>
                <p style='color: #6c757d;'>We're working on adding this feature. Stay tuned for updates!</p>
            </div>
        """, unsafe_allow_html=True)                  

if __name__ == "__main__":
    main()
