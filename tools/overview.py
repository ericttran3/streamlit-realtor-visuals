import streamlit as st
import streamlit_shadcn_ui as ui
import streamlit_antd_components as sac
import pandas as pd
from streamlit_searchbox import st_searchbox
from src.components.charts import (
    create_area_chart,
    create_seasonality_chart,
    create_combo_chart
)
from src.components.metrics import create_metrics_grid
from src.components.tables import create_comparison_table
from src.data.data_loader import (
    METRICS,
    load_dask_data,
    get_unique_locations,
    search_locations
)
from src.config import STYLE_OVERRIDES


def main():
    """Main details page rendering function"""
    # Header section with icon and title
    st.markdown(
        """
        <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 5px;'>
            <h3>Market Overview</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.write("Explore dynamic real estate market trends across national, state, and local markets with the latest data from realtor.com")
    
    # # Description section with key features in an expander
    # with st.expander("Quick Guide", expanded=False):
    #     st.markdown(
    #         """
    #         - 🔍 **Search:** Enter any state, metro area, county, or ZIP code
    #         - ⚡ **Quick Filters:** Use the filter menu to:
    #           - Adjust date ranges (3M, 6M, YTD, 1Y, 5Y, or custom)
    #           - Switch between different views (Value, MoM, YoY, Since 2019, Seasonality)
    #         - 📈 **Visualizations:** Toggle between Charts, Metrics, Summary Table, and Raw Data
    #         """
    #     )

    # ui.tabs(options=['Charts', 'Metrics', 'Table', 'Data'], default_value='Charts', key="tab_shadcn")

    # Load data
    ddf = load_dask_data()
    location_options = get_unique_locations(ddf)

    # Define default locations
    default_locations = [
        "National - United States",
        "State - California",
        "Metro - Los Angeles-Long Beach-Anaheim, CA",
        "County - Los Angeles, CA",
        "Zip - 90001, Los Angeles, CA"
    ]
    
    # Ensure all default locations exist in the options
    default_locations = [loc for loc in default_locations if loc in location_options]
    
    # If no default locations are valid, fall back to the first option
    if not default_locations:
        default_locations = [location_options[0]]

    # Create a container for search and filters
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create search box with default options
        selected_location = st_searchbox(
            search_function=lambda searchterm: search_locations(searchterm, location_options),
            # label="Search Location",
            placeholder="🔍 Search by state, metro, county, or zip code.", #Search any location (e.g., California, Los Angeles Metro, Orange County, 90210
            default=default_locations[0],  # First default location
            default_options=default_locations[1:],  # Show all default locations in dropdown
            key="details_location_search",
            style_overrides=STYLE_OVERRIDES,
        )

    with col2:
        # st.write("Filters")
        with st.popover("Filters", icon=":material/filter_alt:", use_container_width=False):
                
                st.write("##### Advanced Filters")
            
            # Time Period section
            # Calculate date ranges
                min_date = ddf['date'].min().compute()
                max_date = ddf['date'].max().compute()
                current_year = max_date.year
                ytd_start = pd.Timestamp(f"{current_year}-01-01")
                
                periods = {
                    "3M": max_date - pd.DateOffset(months=3),
                    "6M": max_date - pd.DateOffset(months=6),
                    "YTD": ytd_start,
                    "1Y": max_date - pd.DateOffset(years=1),
                    "5Y": max_date - pd.DateOffset(years=5),
                    "Max": min_date
                }
                
                # Initialize selected period in session state if not exists
                if 'selected_period' not in st.session_state:
                    st.session_state.selected_period = "Max"  # Default to 1 year
                
                # Create segmented control for periods
                selected_period = st.segmented_control(
                    label="**Periods**",
                    options=list(periods.keys()),
                    default="Max",
                    key="period_selector_segmented_control",
                    help="Select a period to update the charts below",
                )
                
                # Update session state and date range when selection changes
                if selected_period:
                    st.session_state.selected_period = selected_period
                    st.session_state.custom_date_range = None
                
                # Date Range section
                col_1, col_2 = st.columns([2, 1])
                # Get current date range based on period or previous selection
                if st.session_state.custom_date_range:
                    default_dates = st.session_state.custom_date_range
                else:
                    default_dates = (periods[st.session_state.selected_period], max_date)
                
                with col_1: 
                    # Create date input
                    custom_dates = st.date_input(
                        "**Custom Date Range**",
                        value=default_dates,
                        min_value=min_date.date(),
                        max_value=max_date.date(),
                        key="custom_date_range_input",
                        format="MM/DD/YYYY",
                    )
                    
                    # Update date range based on selection
                    if isinstance(custom_dates, tuple) and len(custom_dates) == 2:
                        # Convert date objects to timestamps
                        date_range = (
                            pd.Timestamp(custom_dates[0]),
                            pd.Timestamp(custom_dates[1])
                        )
                        st.session_state.custom_date_range = date_range
                        st.session_state.selected_period = None
                    else:
                        date_range = default_dates

                with col_2:
                    st.write(" ")

                # Comparison Type section
                
                # Initialize comparison type in session state if not exists
                if 'comparison_type' not in st.session_state:
                    st.session_state.comparison_type = "Value"
                
                # Create segmented control for comparison type
                selected_comparison = st.pills(
                    f"**Views**",
                    options=["Value", "MoM", "YoY", "Since 2019", "Seasonality"],
                    default="Value",
                    key="comparison_views_pills",
                    help="Select a view type to update the charts below"
                )
                
                # Update session state when selection changes
                if selected_comparison:
                    st.session_state.comparison_type = selected_comparison
    
    # Process data first if location is selected
    if selected_location:
        try:
            # Parse location string to get geo_type and name
            geo_type, geo_name = selected_location.split(" - ", 1)
            
            # Get data for the selected location
            if geo_type == 'Zip':
                zip_code = geo_name.split(',')[0]
                filtered_df = ddf[
                    (ddf['geo_type'] == geo_type) & 
                    (ddf['geo_id'] == zip_code)
                ].compute()
                display_name = f"{zip_code}, {geo_name.split(',', 1)[1]}"
            else:
                filtered_df = ddf[
                    (ddf['geo_type'] == geo_type) & 
                    (ddf['geo_name'] == geo_name)
                ].compute()
                display_name = geo_name

            # Get date range info
            if st.session_state.custom_date_range:
                start_date, end_date = st.session_state.custom_date_range
            else:
                end_date = max_date
                start_date = periods[st.session_state.selected_period]

            # Show summary before tabs using shadcn badges
            # st.write("**Current View:**")
            ui.badges(
                badge_list=[
                    (f"🌎  {geo_type}", "secondary"),  # "destructive", "default", "secondary", "outline"
                    (f"📍  {display_name}", "secondary"),  # Location name
                    (f"📅  {start_date.strftime('%B %Y')} - {end_date.strftime('%B %Y')}", "secondary"),  # Date range
                    (f"👁️‍🗨️  {st.session_state.comparison_type} View", "secondary")  # View type
                ],
                class_name="flex gap-2",
                key="current_view_badges"
            )

            # Create tabs after summary
            tab_charts, tab_metrics, tab_table, tab_data = st.tabs([
                "Charts", "Metrics", "Table", "Data"
            ])

            if len(filtered_df) == 0:
                st.warning("No data available for the selected location")
                return

            # Filter data based on selected date range
            filtered_df = filtered_df[
                (filtered_df['date'] >= start_date) & 
                (filtered_df['date'] <= end_date)
            ]
            
            # Sort by date
            filtered_df = filtered_df.sort_values('date')
            
            # Get the selected comparison type
            comparison_type = st.session_state.comparison_type

            # Display content in each tab
            with tab_charts:
                # sac.divider(label='Charts', icon='bar-chart', align='center', color='gray')
                
                # Display charts for each metric
                for i in range(0, len(METRICS), 2):
                    col1, col2 = st.columns(2)
                    
                    # First metric
                    metric_col = list(METRICS.keys())[i]
                    metric_name = METRICS[metric_col]
                    with col1:
                        try:
                            if comparison_type == "Value":
                                chart = create_area_chart(filtered_df, metric_col, metric_name, display_name)
                            elif comparison_type == "Seasonality":
                                chart = create_seasonality_chart(filtered_df, metric_col, metric_name, display_name)
                            else:
                                chart = create_combo_chart(filtered_df, metric_col, metric_name, display_name, comparison_type)
                            st.altair_chart(chart, use_container_width=True)
                        except Exception as e:
                            st.error(f"Error creating chart for {metric_name}: {str(e)}")
                    
                    # Second metric (if exists)
                    if i + 1 < len(METRICS):
                        metric_col = list(METRICS.keys())[i + 1]
                        metric_name = METRICS[metric_col]
                        with col2:
                            try:
                                if comparison_type == "Value":
                                    chart = create_area_chart(filtered_df, metric_col, metric_name, display_name)
                                elif comparison_type == "Seasonality":
                                    chart = create_seasonality_chart(filtered_df, metric_col, metric_name, display_name)
                                else:
                                    chart = create_combo_chart(filtered_df, metric_col, metric_name, display_name, comparison_type)
                                st.altair_chart(chart, use_container_width=True)
                            except Exception as e:
                                st.error(f"Error creating chart for {metric_name}: {str(e)}")

            with tab_metrics:
                create_metrics_grid(filtered_df, display_name, comparison_type)

            with tab_table:
                comparison_map = {
                    "Value": "Value",
                    "MoM": "MoM",
                    "YoY": "YoY",
                    "Since 2019": "Since 2019",
                    "Seasonality": "Seasonality"
                }

                create_comparison_table(
                    df=filtered_df, 
                    display_name=display_name,
                    comparison_type=comparison_map[selected_comparison]
                )

            with tab_data:
                st.dataframe(
                    filtered_df.sort_values('date', ascending=False),
                    hide_index=True,
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"Error processing data: {str(e)}")
            return

if __name__ == "__main__":
    main()

