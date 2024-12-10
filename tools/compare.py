import streamlit as st
import streamlit_shadcn_ui as ui
import pandas as pd
from src.components.charts import create_line_chart  # We'll create this
from src.components.tables import create_comparison_matrix  # We'll create this
from src.data.data_loader import (
    METRICS,
    load_dask_data,
    get_unique_locations
)
from src.config import STYLE_OVERRIDES

def calculate_changes(df, metric_col):
    """Calculate MoM, YoY, and Since 2019 changes for a given metric"""
    latest_value = df[metric_col].iloc[-1]
    
    # Month over Month
    mom = ((latest_value / df[metric_col].iloc[-2] - 1) * 100) if len(df) > 1 else None
    
    # Year over Year
    yoy = ((latest_value / df[metric_col].iloc[-13] - 1) * 100) if len(df) >= 13 else None
    
    # Since 2019
    baseline_2019 = df[df['date'].dt.year == 2019][metric_col].mean()
    since_2019 = ((latest_value / baseline_2019 - 1) * 100) if not pd.isna(baseline_2019) else None
    
    return mom, yoy, since_2019

def format_pct_change(value):
    """Format percentage change with color and sign"""
    if pd.isna(value):
        return "-"
    color = "red" if value < 0 else "green"
    return f"<span style='color: {color}'>{value:+.1f}%</span>"

def compare_page():
    """Main comparison page rendering function"""
    # Header section
    st.markdown(
        """
        <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 5px;'>
            <h3>Market Comparison</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.write("Compare real estate market trends across multiple locations with the latest data from realtor.com. Add up to 5 locations to compare.")
    
    # Load data
    ddf = load_dask_data()
    location_options = get_unique_locations(ddf)

    # Define default locations with LA area focus
    default_locations = [
        "State - California",
        "County - Los Angeles, CA",
        "Metro - Los Angeles-Long Beach-Anaheim, CA",
        # "Zip - 90210, Beverly Hills, CA"
    ]
    
    # Create a container for multi-select and filters
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create multi-select with updated default options
        selected_locations = st.multiselect(
            "Select up to 5 locations to compare",
            options=location_options,
            default=default_locations,
            placeholder="🔍 Search by state, metro, county, or zip code.", 
            max_selections=5,
            key="compare_location_select",
            label_visibility="collapsed"
        )

    with col2:
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
                st.session_state.selected_period = "Max"  # Default to Max
            
            # Create segmented control for periods
            selected_period = st.segmented_control(
                label="**Periods**",
                options=list(periods.keys()),
                default="Max",
                key="period_selector_compare",
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
                    key="custom_date_range_compare",
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

            # Views section with Value always selected
            st.pills(
                f"**Views**",
                options=["Value", "MoM", "YoY", "Since 2019"],
                default="Value",
                key="view_type",
                help="Select a view type to update the charts below"
            )                

    # Process data if locations are selected
    if selected_locations:
        try:
            # Get date range info
            if st.session_state.custom_date_range:
                start_date, end_date = st.session_state.custom_date_range
            else:
                end_date = max_date
                start_date = periods[st.session_state.selected_period]

            # Process all selected locations
            all_data = []
            display_names = []
            
            for location in selected_locations:
                geo_type, geo_name = location.split(" - ", 1)
                
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
                
                filtered_df = filtered_df[
                    (filtered_df['date'] >= start_date) & 
                    (filtered_df['date'] <= end_date)
                ].sort_values('date')
                
                all_data.append(filtered_df)
                display_names.append(display_name)

            # Show summary badges
            ui.badges(
                badge_list=[
                    (f"🌎  {geo_type}", "secondary"),  # "destructive", "default", "secondary", "outline"
                    (f"📍 Comparing {selected_locations}", "secondary"),
                    (f"📅 {start_date.strftime('%B %Y')} - {end_date.strftime('%B %Y')}", "secondary"),
                    (f"👁️‍🗨️  {st.session_state.view_type} View", "secondary")  # View type
                ],
                class_name="flex gap-2",
                key="current_view_badges_compare"
            )

            # Create tabs
            tab_charts, tab_table, tab_data = st.tabs([
                "Charts", "Table", "Data"
            ])

            with tab_charts:
                for i in range(0, len(METRICS), 2):
                    col1, col2 = st.columns(2)
                    
                    # First metric
                    metric_col = list(METRICS.keys())[i]
                    metric_name = METRICS[metric_col]
                    with col1:
                        try:
                            chart = create_line_chart(
                                dfs=all_data,
                                metric_col=metric_col,
                                metric_name=metric_name,
                                display_names=display_names,
                                selected_period=st.session_state.selected_period,
                                view_type=st.session_state.view_type
                            )
                            st.altair_chart(chart, use_container_width=True)
                        except Exception as e:
                            st.error(f"Error creating chart for {metric_name}: {str(e)}")
                    
                    # Second metric (if exists)
                    if i + 1 < len(METRICS):
                        metric_col = list(METRICS.keys())[i + 1]
                        metric_name = METRICS[metric_col]
                        with col2:
                            try:
                                chart = create_line_chart(
                                    dfs=all_data,
                                    metric_col=metric_col,
                                    metric_name=metric_name,
                                    display_names=display_names,
                                    selected_period=st.session_state.selected_period,
                                    view_type=st.session_state.view_type
                                )
                                st.altair_chart(chart, use_container_width=True)
                            except Exception as e:
                                st.error(f"Error creating chart for {metric_name}: {str(e)}")

            with tab_table:
                create_comparison_matrix(
                    dfs=all_data,
                    display_names=display_names
                )

            with tab_data:
                # Combine all dataframes
                combined_df = pd.concat(all_data, ignore_index=True)
                st.dataframe(
                    combined_df.sort_values(['date', 'geo_type', 'geo_name'], ascending=[False, True, True]),
                    hide_index=True,
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"Error processing data: {str(e)}")
            return

if __name__ == "__main__":
    compare_page()

