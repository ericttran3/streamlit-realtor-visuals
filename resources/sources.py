import streamlit as st
import pandas as pd

def display_data_coverage():
    """
    Creates and displays a formatted table showing geographic coverage
    across different real estate data providers.
    """
    
    # Create DataFrame
    df = pd.read_csv("data/real_estate_data_coverage.csv")
    
    # Custom CSS for styling
    st.markdown("""
        <style>
        .stDataFrame {
            font-size: 14px;
        }
        .stDataFrame td {
            font-family: 'Arial', sans-serif;
            padding: 8px;
        }
        .stDataFrame th {
            background-color: #f0f2f6;
            color: #1f1f1f;
            font-weight: 600;
            padding: 10px;
        }
        .stDataFrame tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .stDataFrame tr:hover {
            background-color: #eef0f2;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Display header
    st.header("🗺️ Geographic Coverage")
    st.markdown("""
        <div style='padding: 10px 0px 20px 0px; color: #666;'>
        Geographic coverage comparison across major real estate data providers
        </div>
    """, unsafe_allow_html=True)
    
    # Display the table
    st.dataframe(
        df,
        column_config={
            "Geography": st.column_config.TextColumn(
                "Geography",
                width="small",
                help="Geographic level"
            ),
            "Zillow": st.column_config.TextColumn(
                "Zillow",
                width="small",
                help="Number of geographies covered by Zillow"
            ),
            "Redfin": st.column_config.TextColumn(
                "Redfin",
                width="small",
                help="Number of geographies covered by Redfin"
            ),
            "Realtor": st.column_config.TextColumn(
                "Realtor",
                width="small",
                help="Number of geographies covered by Realtor.com"
            ),
            "Description": st.column_config.TextColumn(
                "Description",
                width="large",
                help="Description of the geographic level"
            ),
        },
        hide_index=True,
        use_container_width=True,
    )
    
    # Add footer with additional information
    st.markdown("""
        <div style='font-size: 14px; color: #666; padding-top: 20px;'>
        <strong>Notes:</strong>
        <ul style='margin-top: 5px;'>
            <li>Empty cells indicate no coverage for that geographic level</li>
            <li>Coverage may vary by metric and region</li>
            <li>Geographic definitions may vary between providers</li>
        </ul>
        </div>
    """, unsafe_allow_html=True)


def display_metrics_table():
    """
    Creates and displays a formatted table showing real estate metrics
    from different sources (Zillow, Redfin, Realtor).
    """
    # Read and process the data
    data = {
        'Source': [],
        'Metric': [],
        'API Name': [],
        'Description': []
    }
    
    # Create DataFrame from the raw data
    try:
        df = pd.read_csv('data/real_estate_data_catalog.csv')
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return
    
    # Rename the 'Zillow' column to 'API Name' for clarity
    df = df.rename(columns={'Zillow': 'API Name'})
    
    # Custom CSS to style the table
    st.markdown("""
        <style>
        .stDataFrame {
            font-size: 14px;
        }
        .stDataFrame td {
            font-family: 'Arial', sans-serif;
            padding: 8px;
        }
        .stDataFrame th {
            background-color: #f0f2f6;
            color: #1f1f1f;
            font-weight: 600;
            padding: 10px;
        }
        .stDataFrame tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .stDataFrame tr:hover {
            background-color: #eef0f2;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Display header with custom formatting
    st.header("📊 Real Estate Data Metrics")
    st.markdown("""
        <div style='padding: 10px 0px 20px 0px; color: #666;'>
        Comprehensive overview of available real estate metrics from major data providers
        </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for search and filter
    col1, col2 = st.columns([2, 1])
    
    # Add search functionality in the first column
    with col1:
        search_term = st.text_input("🔍 Search metrics")
    
    # Add source filter in the second column
    with col2:
        sources = ['All'] + sorted(df['Source'].unique().tolist())
        selected_source = st.selectbox("Filter by Source", sources)
    
    # Filter the dataframe based on search term
    if search_term:
        search_mask = (
            df['Metric'].str.contains(search_term, case=False) |
            df['Description'].str.contains(search_term, case=False) |
            df['Source'].str.contains(search_term, case=False) |
            df['API Name'].str.contains(search_term, case=False)
        )
        df = df[search_mask]
    
    # Filter by source if not "All"
    if selected_source != 'All':
        df = df[df['Source'] == selected_source]
    
    # Display the table with enhanced column configuration
    st.dataframe(
        df,
        column_config={
            "Source": st.column_config.TextColumn(
                "Source",
                width="small",
                help="Data provider name",
            ),
            "Metric": st.column_config.TextColumn(
                "Metric",
                width="medium",
                help="Name of the metric",
            ),
            "API Name": st.column_config.TextColumn(
                "API Name",
                width="small",
                help="API endpoint or parameter name",
            ),
            "Description": st.column_config.TextColumn(
                "Description",
                width="large",
                help="Detailed description of the metric",
            ),
        },
        hide_index=True,
        use_container_width=True,
    )
    
    # Add metrics count summary
    total_metrics = len(df)
    st.markdown(f"""
        <div style='font-size: 14px; color: #666; padding-top: 5px;'>
        Showing {total_metrics} metrics {f"for {selected_source}" if selected_source != 'All' else 'across all sources'}
        </div>
    """, unsafe_allow_html=True)
    
    # Add footer with additional information
    st.markdown("""
        <div style='font-size: 14px; color: #666; padding-top: 20px;'>
        <strong>Notes:</strong>
        <ul style='margin-top: 5px;'>
            <li>API Names are used for programmatic access to these metrics</li>
            <li>Some metrics may not be available for all geographic levels</li>
            <li>Data availability and update frequency may vary by source</li>
        </ul>
        </div>
    """, unsafe_allow_html=True)

def display_data_feeds_table():
    """
    Creates and displays a formatted table showing real estate data feeds
    from different sources with filtering and search capabilities.
    """
    # Read the data
    df = pd.read_csv('data/real_estate_data_feeds.csv')
    
    # Custom CSS for the table
    st.markdown("""
        <style>
        .stDataFrame {
            font-size: 14px;
        }
        .stDataFrame td {
            font-family: 'Arial', sans-serif;
            padding: 8px;
        }
        .stDataFrame th {
            background-color: #f0f2f6;
            color: #1f1f1f;
            font-weight: 600;
            padding: 10px;
        }
        .stDataFrame tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .stDataFrame tr:hover {
            background-color: #eef0f2;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Display header
    st.header("📿 Real Estate Data Feeds")
    st.markdown("""
        <div style='padding: 10px 0px 20px 0px; color: #666;'>
        Comprehensive listing of available real estate data feeds and their update schedules
        </div>
    """, unsafe_allow_html=True)
    
    # Create three columns for filters
    col1, col2, col3 = st.columns([2, 1, 1])
    
    # Add search functionality in the first column with a unique key
    with col1:
        search_term = st.text_input(
            "🔍 Search metrics",
            key="data_feeds_search"  # Added unique key
        )
    
    # Add source filter in the second column with a unique key
    with col2:
        sources = ['All'] + sorted(df['Source'].unique().tolist())
        selected_source = st.selectbox(
            "Filter by Source",
            sources,
            key="data_feeds_source"  # Added unique key
        )
    
    # Add geography filter in the third column with a unique key
    with col3:
        geos = ['All'] + sorted(df['Geo'].unique().tolist())
        selected_geo = st.selectbox(
            "Filter by Geography",
            geos,
            key="data_feeds_geo"  # Added unique key
        )
    
    # Filter the dataframe based on search term
    if search_term:
        search_mask = (
            df['Metric'].str.contains(search_term, case=False) |
            df['Source'].str.contains(search_term, case=False) |
            df['Geo'].str.contains(search_term, case=False)
        )
        df = df[search_mask]
    
    # Filter by source if not "All"
    if selected_source != 'All':
        df = df[df['Source'] == selected_source]
        
    # Filter by geography if not "All"
    if selected_geo != 'All':
        df = df[df['Geo'] == selected_geo]
    
    # Create a clickable link for the endpoint
    # df['Endpoint'] = df['Endpoint'].apply(lambda x: f'<a href="{x}" target="_blank">{x}</a>')
    
    # Display the table with enhanced column configuration
    st.dataframe(
        df,
        column_config={
            "Source": st.column_config.TextColumn(
                "Source",
                width="small",
                help="Data provider name",
            ),
            "Metric": st.column_config.TextColumn(
                "Metric",
                width="medium",
                help="Name of the metric",
            ),
            "Geo": st.column_config.TextColumn(
                "Geography",
                width="small",
                help="Geographic level of the data",
            ),
            "Endpoint": st.column_config.LinkColumn(
                "Endpoint",
                width="small",
                help="Data feed URL",
            ),
            "Freshness": st.column_config.DateColumn(
                "Data Freshness",
                width="small",
                help="Most recent data period available",
                format="MMM DD, YYYY",
            ),
            "Last Updated": st.column_config.DateColumn(
                "Last Updated",
                width="small",
                help="Date of last update",
                format="MMM DD, YYYY",
            ),
            "Next Update": st.column_config.DateColumn(
                "Next Update",
                width="small",
                help="Expected date of next update",
                format="MMM DD, YYYY",
            ),
        },
        hide_index=True,
        use_container_width=True,
    )
    
    # Add metrics count summary
    total_metrics = len(df)
    source_text = f"for {selected_source}" if selected_source != 'All' else "across all sources"
    geo_text = f"in {selected_geo} geographies" if selected_geo != 'All' else "across all geographies"
    
    st.markdown(f"""
        <div style='font-size: 14px; color: #666; padding-top: 0px;'>
        Showing {total_metrics} data feeds {source_text} {geo_text}
        </div>
    """, unsafe_allow_html=True)
    
    # Add footer with additional information
    st.markdown("""
        <div style='font-size: 14px; color: #666; padding-top: 20px;'>
        <strong>Notes:</strong>
        <ul style='margin-top: 5px;'>
            <li>All timestamps are in UTC</li>
            <li>Update schedules may vary during holidays</li>
            <li>Click on endpoints to download the data directly</li>
        </ul>
        </div>
    """, unsafe_allow_html=True)

# Example usage:
if __name__ == "__main__":
    display_data_coverage()
    display_metrics_table()
    display_data_feeds_table()
