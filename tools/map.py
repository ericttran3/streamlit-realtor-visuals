import streamlit as st
import streamlit_shadcn_ui as ui
import folium
from streamlit_folium import st_folium
import pandas as pd
from src.data.data_loader import METRICS, load_dask_data

__all__ = ['render_map_view']

def format_metric_value(value):
    if isinstance(value, (int, float)):
        return f"{value:,.0f}"
    else:
        return str(value)

def render_map_view():
    # Header section with icon and title
    st.markdown(
        """
        <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 5px;'>
            <h3>Map</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.write("Explore real estate metrics across different geographic regions with latest data from realtor.com")
        
    
    try:
        # Load data
        ddf = load_dask_data()
        available_dates = sorted(ddf['date'].unique().compute())
        
        # Create two columns for controls
        col1, col2 = st.columns([2, 1])
        
        # First column: Metric selector
        with col1:
            selected_metric = st.selectbox(
                "Select Metric",
                options=list(METRICS.values()),
                label_visibility="collapsed"
            )
            metric_col = next(k for k, v in METRICS.items() if v == selected_metric)
        
        # Second column: Filters popover
        with col2:
            with st.popover("Filters", icon=":material/filter_alt:", use_container_width=False):
                st.write("##### Advanced Filters")
                
                # Date slider
                selected_date = st.select_slider(
                    "**Date Range**",
                    options=available_dates,
                    value=available_dates[-1],
                    format_func=lambda x: x.strftime('%B %Y'),
                    help="Select a date range to update the map below"
                )
                
                # View type pills
                selected_comparison = st.pills(
                    "**Views**",
                    options=["Value", "MoM", "YoY", "Since 2019"],
                    default="Value",
                    key="map_views_pills",
                    help="Select a view type to update the map below"
                )
        
        # Show summary badges using shadcn
        ui.badges(
            badge_list=[
                (f"🌎  State", "outline"),
                (f"📅  {selected_date.strftime('%B %Y')}", "default"),
                (f"👁️‍🗨️  {selected_metric} ({selected_comparison})", "destructive")
            ],
            class_name="flex gap-2",
            key="current_view_badges_map"
        )
        
        # Load data
        ddf = load_dask_data()
        
        # Get all available dates
        available_dates = sorted(ddf['date'].unique().compute())
        
        # Create the base map first
        m = folium.Map(
            location=[39.8283, -98.5795],
            zoom_start=4,
            tiles='cartodbpositron',
            width='100%'
        )
        
        # Filter and process data based on comparison type
        df_states = ddf[ddf['geo_type'] == 'State'].compute()
        
        if selected_comparison == "Value":
            df_states = df_states[df_states['date'] == selected_date]
        elif selected_comparison == "MoM":
            # Calculate Month over Month change
            current = df_states[df_states['date'] == selected_date]
            previous = df_states[df_states['date'] == (selected_date - pd.DateOffset(months=1))]
            df_states = calculate_percent_change(current, previous, metric_col)
        elif selected_comparison == "YoY":
            # Calculate Year over Year change
            current = df_states[df_states['date'] == selected_date]
            previous = df_states[df_states['date'] == (selected_date - pd.DateOffset(years=1))]
            df_states = calculate_percent_change(current, previous, metric_col)
        elif selected_comparison == "Since 2019":
            # Calculate change since same month in 2019
            current = df_states[df_states['date'] == selected_date]
            baseline_date = pd.Timestamp(f"2019-{selected_date.month:02d}-01")
            baseline = df_states[df_states['date'] == baseline_date]
            df_states = calculate_percent_change(current, baseline, metric_col)
        
        
        # Verify data exists
        if len(df_states) == 0:
            st.warning("No data available for the selected date")
            return
            
        if metric_col not in df_states.columns:
            st.error(f"Selected metric '{metric_col}' not found in data")
            return
            
        # Create choropleth layer
        choropleth = folium.Choropleth(
            geo_data='https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json',
            name='choropleth',
            data=df_states,
            columns=['geo_id', metric_col],
            key_on='feature.id',
            fill_color=(
                'YlOrRd' if selected_comparison == "Value" else  # Yellow to Red for values
                'RdYlBu' if selected_comparison in ["MoM", "YoY", "Since 2019"] else  # Red-Yellow-Blue for comparisons
                'YlOrRd'  # Default fallback
            ),
            fill_opacity=0.8,
            line_opacity=0.2,
            legend_name=f"{selected_metric} ({selected_date.strftime('%B %Y')})",
            highlight=True,
            legend=True,
            bins=8,
            legend_kwds={
                'caption': f"{selected_metric} ({selected_date.strftime('%B %Y')})",
                'position': 'bottomleft',
                'orientation': 'horizontal'
            }
        ).add_to(m)
        
        # Add hover functionality
        style_function = lambda x: {
            'fillColor': '#ffffff',
            'color': '#000000',
            'fillOpacity': 0.0,
            'weight': 0.5
        }
        
        highlight_function = lambda x: {
            'fillColor': '#000000',
            'color': '#000000',
            'fillOpacity': 0.2,
            'weight': 1
        }
        
        # Create a mapping of state FIPS to state data
        state_data = df_states.set_index('geo_id').to_dict(orient='index')
        
        # Add the choropleth data to the GeoJSON for tooltips
        for feature in choropleth.geojson.data['features']:
            state_id = feature['id']
            if state_id in state_data:
                feature['properties'].update({
                    'metric_value': format_metric_value(state_data[state_id][metric_col]),
                    'date': state_data[state_id]['date'].strftime('%B %Y'),
                    'geo_name': feature['properties']['name']
                })
        
        # Add GeoJson layer for tooltips
        folium.GeoJson(
            data=choropleth.geojson.data,
            style_function=style_function,
            control=False,
            highlight_function=highlight_function,
            tooltip=folium.GeoJsonTooltip(
                fields=['date', 'geo_name', 'metric_value'],
                aliases=['Date:', 'Location:', f'{selected_metric}:'],
                style=('background-color: white; '
                      'color: #333333; '
                      'font-family: arial; '
                      'font-size: 12px; '
                      'padding: 10px;'),
                sticky=True
            )
        ).add_to(m)
        
        # Display the map
        st_folium(
            m,
            width="100%",
            height=700,
            returned_objects=[]
        )
        
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        st.write("Debug info:")
        st.write(f"Selected metric: {selected_metric}")
        st.write(f"Metric column: {metric_col}")
        
        # If df_states exists, show its info
        if 'df_states' in locals():
            st.write("DataFrame info:")
            st.write(df_states.info())

def calculate_percent_change(current_df, previous_df, metric_col):
    """Calculate percent change between two periods.
    
    Returns the percentage change: ((current - baseline) / baseline) * 100
    For example: if baseline is 100 and current is 120, returns +20%
    """
    # Merge current and previous periods
    merged = current_df.merge(
        previous_df[['geo_id', metric_col]],
        on='geo_id',
        suffixes=('', '_prev')
    )
    
    # Calculate percent change
    # Formula: ((current - baseline) / baseline) * 100
    merged[metric_col] = ((merged[metric_col] - merged[f"{metric_col}_prev"]) / 
                         merged[f"{metric_col}_prev"] * 100)
    
    return merged
