# At the top of overview.py
import streamlit as st
import altair as alt
from vega_datasets import data
import json
import pandas as pd
from typing import Dict, List, Tuple, Optional
import warnings
import numpy as np
warnings.filterwarnings('ignore')  # Suppress warnings from Altair

# State to FIPS code mapping
STATE_TO_FIPS = {
    'AL': '01', 'AK': '02', 'AZ': '04', 'AR': '05', 'CA': '06', 'CO': '08', 'CT': '09',
    'DE': '10', 'FL': '12', 'GA': '13', 'HI': '15', 'ID': '16', 'IL': '17', 'IN': '18',
    'IA': '19', 'KS': '20', 'KY': '21', 'LA': '22', 'ME': '23', 'MD': '24', 'MA': '25',
    'MI': '26', 'MN': '27', 'MS': '28', 'MO': '29', 'MT': '30', 'NE': '31', 'NV': '32',
    'NH': '33', 'NJ': '34', 'NM': '35', 'NY': '36', 'NC': '37', 'ND': '38', 'OH': '39',
    'OK': '40', 'OR': '41', 'PA': '42', 'RI': '44', 'SC': '45', 'SD': '46', 'TN': '47',
    'TX': '48', 'UT': '49', 'VT': '50', 'VA': '51', 'WA': '53', 'WV': '54', 'WI': '55',
    'WY': '56', 'DC': '11'
}

# Available metrics for visualization
METRICS = [
    ("active_listing_count", "Active Listing Count"), 
    ("new_listing_count", "New Listing Count"),
    ("pending_listing_count", "Pending Listing Count"),
    ("total_listing_count", "Total Listing Count"),
    ("pending_ratio", "Pending Ratio"),
    ("median_listing_price", "Median Listing Price"),
    ("average_listing_price", "Average Listing Price"),
    ("median_square_feet", "Median Square Feet"),
    ("median_listing_price_per_square_foot", "Price per Square Foot"),
    ("median_days_on_market", "Median Days on Market"),
    ("price_increased_count", "Price Increased Count"),
    ("price_reduced_count", "Price Reduced Count"),
]

# Geo Mappings
GEO_MAPPINGS = {
    "Country": {
        "id_col": None,
        "name_col": "country",
        "display_name": "Country"
    },
    "State": {
        "id_col": "state_id",  # This should match your CSV column name
        "name_col": "state",   # This should match your CSV column name
        "display_name": "State"
    },
    "Metro": {
        "id_col": "cbsa_code",
        "name_col": "cbsa_title",
        "display_name": "Metro Area"
    },
    "County": {
        "id_col": "county_fips",
        "name_col": "county_name",
        "display_name": "County"
    },
    "Zip": {
        "id_col": "postal_code",
        "name_col": "zip_name",
        "display_name": "ZIP Code"
    }
}

GEO_LEVELS = list(GEO_MAPPINGS.keys())

# Add at the top with other constants
CHART_DEFAULTS = {
    'width': 500,
    'height': 300,
    'font_size': 16,
    'color_scheme': 'yellowgreenblue'
}

MAP_STYLES = {
    'metro': {'stroke': 'blue', 'strokeWidth': 0.5},
    'state': {'stroke': 'black', 'strokeWidth': 1},
    'highlight': {'stroke': 'red', 'strokeWidth': 3}
}

################################################################################

@st.cache_data
def load_geometries():
    """Load all geographic boundary data"""
    try:
        with open('data/realtor/2015-cbsa-no-properties.geojson', 'r') as f:
                metros_geojson = json.load(f)

        return {
            'states': alt.topo_feature(data.us_10m.url, 'states'),
            'counties': alt.topo_feature(data.us_10m.url, 'counties'),
            'countries': alt.topo_feature(data.world_110m.url, 'countries'),
            'metros': metros_geojson,
            # 'zipcodes': alt.topo_feature('data/realtor/us_zip_codes.json', 'zip_codes_for_the_usa'),
        }
    except Exception as e:
        st.error(f"Error loading geometries: {str(e)}")
        return None


################################################################################

def display_coming_soon():
    """Display a coming soon message with styling."""
    st.markdown("""
        <div style='padding: 2rem; background-color: #f8f9fa; border-radius: 0.5rem; text-align: center;'>
            <h3 style='color: #6c757d;'>🚧 Coming Soon! 🚧</h3>
            <p style='color: #6c757d;'>We're working on adding this feature. Stay tuned for updates!</p>
        </div>
    """, unsafe_allow_html=True)


# Combine format_value and get_tooltip_format into a single formatting utility class
class MetricFormatter:
    @staticmethod
    def get_tooltip_format(metric: str) -> str:
        if metric == 'pending_ratio':
            return '.1f'
        elif metric.endswith('_mm') or metric.endswith('_yy'):
            return '.1%'
        elif 'price' in metric:
            return '$,.0f'
        return ',.0f'

    @staticmethod
    def format_value(value: float, metric: str) -> str:
        if value is None:
            return "N/A"
        if 'price' in metric:
            return f"${value:,.0f}"
        elif metric in ['pending_ratio'] or metric.endswith(('_mm', '_yy')):
            return f"{value:.1f}%"
        return f"{value:,.0f}"


def get_range_text(data, metric):
    """Get formatted range text based on metric type"""
    state_count = data[data[metric].notna()][metric].count()
    min_val = data[metric].min()
    max_val = data[metric].max()
    
    if metric.endswith('_mm') or metric.endswith('_yy'):
        min_formatted = f"{min_val * 100:.1f}%"
        max_formatted = f"{max_val * 100:.1f}%"
    elif metric == 'pending_ratio':
        min_formatted = f"{min_val:.1f}%"
        max_formatted = f"{max_val:.1f}%"
    else:
        min_formatted = f"{min_val:,.0f}"
        max_formatted = f"{max_val:,.0f}"
    
    return [f"{state_count} states, ranging from {min_formatted} to {max_formatted}"]


def get_metric_format(metric: str) -> str:
    """Return the appropriate format string based on metric type."""
    
    # Metrics that need dollar formatting
    dollar_metrics = {
        'median_listing_price',
        'average_listing_price',
        'median_listing_price_per_square_foot'
    }
    
    # Metrics that need percentage formatting
    percentage_metrics = {
        'pending_ratio'
    }
    
    if metric in dollar_metrics:
        return '$,.0f'
    elif metric in percentage_metrics:
        return '.2f'
    else:
        return ',.0f'  # Regular number formatting for count metrics


def get_comparison_color(value: float, comparison_type: str) -> str:
    """Return appropriate color based on comparison value"""
    if comparison_type == "Value":
        return 'lightgray'  # Default blue
    return "#52be80" if value > 0 else "#ec7063"  # Green for positive, red for negative



def calculate_changes(df: pd.DataFrame, metric: str, view_type: str) -> pd.DataFrame:
    """Calculate metric changes based on view type."""
    df = df.copy()
    
    if view_type == "MoM":
        df[metric] = df[metric].pct_change() * 100
    elif view_type == "YoY":
        df[metric] = (df[metric] - df[metric].shift(12)) / df[metric].shift(12) * 100
    elif view_type == "Since 2019":
        baseline_2019 = df[df['date'].dt.year == 2019].copy()
        baseline_2019['month'] = baseline_2019['date'].dt.month
        df['month'] = df['date'].dt.month
        
        df = df.merge(
            baseline_2019[['month', metric]],
            on='month',
            suffixes=('', '_2019')
        )
        df[metric] = ((df[metric] - df[f'{metric}_2019']) / df[f'{metric}_2019']) * 100
        
    return df


def calculate_comparison_value(df: pd.DataFrame, metric: str, comparison_type: str) -> float:
    """Calculate value based on comparison type."""
    latest_date = df['date'].max()
    latest_value = df[df['date'] == latest_date][metric].iloc[0]
    
    if comparison_type == "Value":
        return latest_value
    
    # Calculate previous date for comparison
    if comparison_type == "MoM":
        prev_date = latest_date - pd.DateOffset(months=1)
    else:  # YoY
        prev_date = latest_date - pd.DateOffset(years=1)
        
    prev_date = df['date'].where(df['date'] <= prev_date).max()
    prev_value = df[df['date'] == prev_date][metric].iloc[0]
    
    # Calculate percentage change
    pct_change = ((latest_value - prev_value) / prev_value) * 100
    return pct_change


## Area Chart
def create_area_chart(df: pd.DataFrame, metric: str, title: str, geo_name: str) -> alt.Chart:
    """Create an area chart for the selected metric with a single tooltip along the x-axis and a vertical line indicator."""
    
    # Selection for hover interaction
    nearest = alt.selection_single(
        nearest=True,
        on='mouseover',
        fields=['date'],
        empty='none',
        clear='mouseout'
    )

    # Base area chart
    area_chart = alt.Chart(df).mark_area(
        line={'color': 'black'},
        color=alt.Gradient(
            gradient='linear',
            stops=[
                alt.GradientStop(color='white', offset=0),
                alt.GradientStop(color='lightgray', offset=1)
            ],
            x1=1,
            x2=1,
            y1=1,
            y2=0
        )
    ).encode(
        x=alt.X(
            'date:T', 
            title=None,
            axis=alt.Axis(
                format="%Y",  # Formatting years
                # grid=True  # Remove vertical grid lines
            )
        ),
        y=alt.Y(
            f'{metric}:Q',
            title=None,
            scale=alt.Scale(zero=False),
            axis=alt.Axis(
                format='~s',  # Use "~s" to format large numbers in a shorter way (e.g., 1.5M instead of 1,500,000)
                # grid=False  # Remove vertical grid lines
            )
        )
    )

    # Selector to allow user to interact with the chart
    selectors = alt.Chart(df).mark_rule(opacity=0).encode(
        x='date:T'
    ).add_selection(nearest)

    # Vertical rule to follow the mouse movement
    rules = alt.Chart(df).mark_rule(color='gray', opacity=0.5).encode(
        x='date:T'
    ).transform_filter(nearest)

    # Points that appear on hover
    points = area_chart.mark_point(
        color='black',
        size=50,
        filled=True,
        opacity=0.5
    ).transform_filter(nearest)

    # Label for the last value
    last_value = df[df['date'] == df['date'].max()]
    last_label = alt.Chart(last_value).mark_text(
        align='center',
        # dx=-10,
        dy=-30,
        fontSize=12,
        fontWeight='bold',
        color='black'
    ).encode(
        x='date:T',
        y=alt.Y(f'{metric}:Q'),
        text=alt.Text(f'{metric}:Q', format=',.2f' if metric == "pending_ratio" else ',.0f')  # Conditional formatting
    )

    # Combine area chart, selectors, rules, points, and last value label into a single chart
    layered_chart = alt.layer(
        area_chart,
        selectors,
        rules,
        points,
        last_label
    ).encode(
        tooltip=[
            alt.Tooltip('date:T', title='Date', format='%b %Y'),
            alt.Tooltip(f'{metric}:Q', title=title, format=',.2f' if metric == "pending_ratio" else ',.0f')
        ]
    ).properties(
        height=300,
        width='container',
        title={
            "text": f"{title}",
            "subtitle": [f"{geo_name}"],
            "color": "black",
            "subtitleColor": "gray",
            "fontSize": 16,
            "subtitleFontSize": 12,
            "anchor": "start"
        }
    ).configure_view(
        stroke=None
    )

    return layered_chart

## Bar Chart
def create_change_bar_chart(df: pd.DataFrame, metric: str, title: str, geo_name: str, view_type: str) -> alt.Chart:
    """Create a bar chart for MoM, YoY, and Since 2019 views."""
    df = calculate_changes(df, metric, view_type)
    
    # Selection for hover interaction
    nearest = alt.selection_single(
        nearest=True,
        on='mouseover',
        fields=['date'],
        empty='none',
        clear='mouseout'
    )

    # Base bar chart
    bars = alt.Chart(df).mark_bar(
        width=2  # Adjust bar width as needed
        ).encode(
        x=alt.X('date:T', title=None),
        y=alt.Y(
            f'{metric}:Q',
            title=None,
            scale=alt.Scale(zero=True)
        ),
        color=alt.condition(
            alt.datum[metric] > 0,
            alt.value("#52be80"),  # green for positive
            alt.value("#ec7063")   # red for negiative
        )
    )
    
    # Selector rule
    selectors = alt.Chart(df).mark_rule(opacity=0).encode(
        x='date:T'
    ).add_selection(nearest)

    # Vertical rule
    rules = alt.Chart(df).mark_rule(color='gray', opacity=0.5).encode(
        x='date:T'
    ).transform_filter(nearest)
    
    # Combine layers
    layered_chart = alt.layer(
        bars,
        selectors,
        rules
    ).encode(
        tooltip=[
            alt.Tooltip('date:T', title='Date', format='%b %Y'),
            alt.Tooltip(f'{metric}:Q', title=title, format='+.2f')
        ]
    ).properties(
        height=300,
        width='container',
        title={
            "text": f"{title} (Change {view_type})",
            "subtitle": [f"{geo_name}"],
            "color": "black",
            "subtitleColor": "gray",
            "fontSize": 16,
            "subtitleFontSize": 12,
            "anchor": "start"
        }
    ).configure_view(
        stroke=None
    )
    
    return layered_chart

## Stacked Line Chart
def create_seasonality_chart(df: pd.DataFrame, metric: str, title: str, geo_name: str) -> alt.Chart:
    """Create a line chart showing seasonal patterns by year with colorblind-friendly colors."""
    dff = df.copy()

    # Define month order
    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Extract year and month
    dff['year'] = dff['date'].dt.year
    dff['month'] = pd.Categorical(
        dff['date'].dt.strftime('%b'),
        categories=month_order,
        ordered=True
    )
    
    # Filter for last 6 years and sort
    current_year = dff['year'].max()
    dff = dff[dff['year'] >= current_year - 5]
    dff['month_num'] = dff['date'].dt.month
    dff = dff.sort_values(['year', 'month_num'])
    
    # Create pivot table for years
    lookup_df = dff.pivot(
        index='month',
        columns='year',
        values=metric
    ).reset_index()
    
    # Ensure proper month ordering
    lookup_df['month'] = pd.Categorical(
        lookup_df['month'],
        categories=month_order,
        ordered=True
    )
    lookup_df = lookup_df.sort_values('month')
    
    # Colorblind-friendly palette with color names for tooltip
    colors = {
        current_year - 5: {'color': '#A6CEE3', 'name': '🔵'},  # light blue
        current_year - 4: {'color': '#B2DF8A', 'name': '🟢'},  # light green
        current_year - 3: {'color': '#FB9A99', 'name': '🔴'},  # light red
        current_year - 2: {'color': '#FDBF6F', 'name': '🟡'},  # light orange
        current_year - 1: {'color': '#CAB2D6', 'name': '🟣'},  # light purple
        current_year: {'color': '#000000', 'name': '⚫'}       # black
    }
    
    # Add color information to the dataframe
    dff['color_name'] = dff['year'].map(lambda x: colors[x]['name'])

    # Create vertical month grid lines
    month_grid = alt.Chart(pd.DataFrame({'month': month_order})).mark_rule(
        strokeDash=[2, 2],
        stroke='#F8F8F8',  # Even lighter gray
        strokeWidth=0.5,    # Thinner lines
        opacity=0.5        # More transparent
    ).encode(
        x=alt.X('month:O', sort=month_order)
    )
    
    # Create base chart for previous years
    previous_years = alt.Chart(dff[dff['year'] < current_year]).mark_line(
        strokeWidth=1.5,
        opacity=0.7
    ).encode(
        x=alt.X('month:O',
                title=None,
                sort=month_order,
                axis=alt.Axis(
                    labelAngle=0,
                    grid=False  # Turn off default grid
                )),
        y=alt.Y(f'{metric}:Q',
                title=None,
                scale=alt.Scale(zero=False),
                axis=alt.Axis(
                    format='~s', 
                    orient='left',
                    grid=True,  # Keep horizontal grid
                    gridDash=[2, 2],
                    gridColor='#EEEEEE'
                )),
        color=alt.Color('year:O',
                       scale=alt.Scale(
                           domain=list(range(current_year-5, current_year)),
                           range=[colors[year]['color'] for year in range(current_year-5, current_year)]
                       ),
                       legend=None),
        detail='year:N'
    )
    
    # Create chart for current year (black line)
    current_year_line = alt.Chart(dff[dff['year'] == current_year]).mark_line(
        strokeWidth=2,
        color='#000000'
    ).encode(
        x=alt.X('month:O', sort=month_order),
        y=alt.Y(f'{metric}:Q')
    )
    
    # Selection rule
    nearest = alt.selection_single(
        nearest=True,
        on="mouseover",
        fields=['month'],
        empty="none",
        clear="mouseout"
    )
    
    # Selectors
    selectors = alt.Chart(lookup_df).mark_rule(
        color='gray',
        strokeWidth=0.5,
        opacity=0.5
    ).encode(
        x=alt.X('month:O', sort=month_order)
    ).add_selection(nearest)
    
    # Points for current year
    points = current_year_line.mark_point(
        filled=True,
        size=60,
        opacity=1,
        color='#000000'
    ).encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )
    
    # Get the appropriate format for this metric
    format_str = get_metric_format(metric)
    
    # Create tooltip with color indicators
    tooltips = [
        alt.Tooltip('month:O', title='Month')
    ]
    
    # Add tooltips for each year with color indicators and appropriate formatting
    for year in sorted(dff['year'].unique(), reverse=True):
        color_name = colors[year]['name']
        tooltip_title = f'{color_name} {year}'
        
        tooltips.append(
            alt.Tooltip(
                f'{year}:Q',
                title=tooltip_title,
                format=format_str
            )
        )
    
    # Create end labels for each year
    year_end_data = []
    for year in dff['year'].unique():
        year_data = dff[dff['year'] == year]
        latest_month = year_data['month_num'].max()
        latest_data = year_data[year_data['month_num'] == latest_month].iloc[0]
        year_end_data.append({
            'month': latest_data['month'],
            'year': year,
            metric: latest_data[metric]
        })
    
    labels_df = pd.DataFrame(year_end_data)
    
    # Create labels for previous years
    previous_years_labels = alt.Chart(labels_df[labels_df['year'] < current_year]).mark_text(
        align='left',
        baseline='middle',
        fontSize=11,
        dx=5
    ).encode(
        x=alt.X('month:O', sort=month_order),
        y=f'{metric}:Q',
        text='year:N',
        color=alt.Color('year:O',
                       scale=alt.Scale(
                           domain=list(range(current_year-5, current_year)),
                           range=[colors[year]['color'] for year in range(current_year-5, current_year)]
                       ))
    )
    
    # Create label for current year
    current_year_label = alt.Chart(labels_df[labels_df['year'] == current_year]).mark_text(
        align='left',
        baseline='middle',
        fontSize=11,
        fontWeight='bold',
        color='#000000',
        dx=5
    ).encode(
        x=alt.X('month:O', sort=month_order),
        y=f'{metric}:Q',
        text='year:N'
    )
    
    # Combine all layers
    chart = alt.layer(
        month_grid,  # Add grid as bottom layer
        previous_years,
        current_year_line,
        selectors,
        points,
        previous_years_labels,
        current_year_label
    ).transform_pivot(
        'year',
        value=metric,
        groupby=['month']
    ).encode(
        tooltip=tooltips
    ).properties(
        height=300,
        width='container',
        title={
            "text": f"{title}",
            "subtitle": [f"{geo_name}"],
            "color": "black",
            "subtitleColor": "gray",
            "fontSize": 16,
            "subtitleFontSize": 12,
            "anchor": "start"
        }
    ).configure_view(
        strokeWidth=0
    )
    
    return chart

## Dual Axis Chart
def create_combo_chart(df: pd.DataFrame, metric: str, title: str, geo_name: str, comparison_type: str) -> alt.Chart:
    """Create a combo chart with metric value line and comparison bars."""
    df = df.copy()
    
    # Calculate comparison values based on type
    if comparison_type == "MoM":
        df['comparison'] = df[metric].pct_change() * 100
        comparison_label = "MoM Change (%)"
    elif comparison_type == "YoY":
        df['comparison'] = (df[metric] - df[metric].shift(12)) / df[metric].shift(12) * 100
        comparison_label = "YoY Change (%)"
    elif comparison_type == "Since 2019":
        baseline_2019 = df[df['date'].dt.year == 2019].copy()
        baseline_2019['month'] = baseline_2019['date'].dt.month
        df['month'] = df['date'].dt.month
        df = df.merge(baseline_2019[['month', metric]], on='month', suffixes=('', '_2019'))
        df['comparison'] = ((df[metric] - df[f'{metric}_2019']) / df[f'{metric}_2019']) * 100
        comparison_label = "Change Since 2019 (%)"
    
    # Selection for hover interaction
    nearest = alt.selection_single(
        nearest=True,
        on='mouseover',
        fields=['date'],
        empty='none',
        clear='mouseout'
    )
    
    # Base chart
    base = alt.Chart(df).encode(
        x=alt.X('date:T', 
                title=None,
                axis=alt.Axis(grid=False)
                )
    )
    
    # Value line
    line = base.mark_line(
        color='black',
        strokeWidth=2
    ).encode(
        y=alt.Y(
            f'{metric}:Q',
            title=None,
            axis=alt.Axis(
                format='~s',
                grid=True,
                gridDash=[2, 2],
                tickCount=5,
                # domain=True,
                ticks=False,
                orient='left'
            )
        )
    )
    
    # Comparison bars
    bars = base.mark_bar(opacity=0.3, width=2).encode(
        y=alt.Y(
            'comparison:Q',
            title=None,
            axis=None
        ),
        color=alt.condition(
            alt.datum.comparison > 0,
            alt.value("#52be80"),
            alt.value("#ec7063")
        )
    )
    
    # Interactive elements
    selectors = base.mark_rule(opacity=0).encode(
        x='date:T'
    ).add_selection(nearest)
    points = line.mark_point(
        color='black',
        size=100,
        filled=True,
        opacity=0
    ).encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    # Vertical rule
    rules = base.mark_rule(color='gray', opacity=0.5).encode(
        x='date:T'
    ).transform_filter(nearest)
    
    # Format tooltips
    format_str = get_metric_format(metric)
    tooltips = [
        alt.Tooltip('date:T', title='Date', format='%b %Y'),
        alt.Tooltip(f'{metric}:Q', title='Value', 
                   format=format_str.replace('$', '') if '$' in format_str else format_str),
        alt.Tooltip('comparison:Q', title=comparison_label, format='+.2f')
    ]
    
    # Combine layers
    chart = alt.layer(
        bars,
        line,
        selectors,
        points,
        rules,
    ).encode(
        tooltip=tooltips
    ).properties(
        height=300,
        width='container',
        title={
            "text": f"{title}",
            "subtitle": [f"{geo_name}"],
            "color": "black",
            "subtitleColor": "gray",
            "fontSize": 16,
            "subtitleFontSize": 12,
            "anchor": "start"
        }
    ).resolve_scale(
        y='independent'
    )
    
    return chart


## Grid
def create_metrics_view(df: pd.DataFrame, metric: str, title: str, comparison_type: str = "Value") -> tuple:
    """
    Create metrics view showing value and comparison change.
    
    Parameters:
    df (pandas.DataFrame): DataFrame with date and metric columns
    metric (str): Name of the metric column
    title (str): Display title for the metric
    comparison_type (str): Type of comparison ("Value", "MoM", "YoY", "Since 2019")
    
    Returns:
    tuple: (formatted_value, delta, delta_color)
    """
    # Get the latest value
    latest_date = df['date'].max()
    latest_value = df[df['date'] == latest_date][metric].iloc[0]
    
    # Format the current value
    format_str = get_metric_format(metric)
    if format_str == '$,.0f':
        formatted_value = f"${latest_value:,.0f}"
    elif format_str == '.1f':
        formatted_value = f"{latest_value:.1f}%"
    else:
        formatted_value = f"{latest_value:,.0f}"
    
    # Calculate delta based on comparison type
    if comparison_type == "Value":
        return formatted_value, None, "off"
        
    elif comparison_type == "MoM":
        prev_date = latest_date - pd.DateOffset(months=1)
        prev_date = df['date'].where(df['date'] <= prev_date).max()
        if prev_date:
            prev_value = df[df['date'] == prev_date][metric].iloc[0]
            delta = ((latest_value - prev_value) / prev_value) * 100
            return formatted_value, f"{delta:+.1f}%", "normal"
        return formatted_value, None, "off"
            
    elif comparison_type == "YoY":
        year_ago_date = latest_date - pd.DateOffset(years=1)
        year_ago_date = df['date'].where(df['date'] <= year_ago_date).max()
        if year_ago_date:
            year_ago_value = df[df['date'] == year_ago_date][metric].iloc[0]
            delta = ((latest_value - year_ago_value) / year_ago_value) * 100
            return formatted_value, f"{delta:+.1f}%", "normal"
        return formatted_value, None, "off"
            
    elif comparison_type == "Since 2019":
        baseline_2019 = df[df['date'].dt.year == 2019]
        if not baseline_2019.empty:
            current_month = latest_date.month
            baseline_value = baseline_2019[baseline_2019['date'].dt.month == current_month][metric].iloc[0]
            delta = ((latest_value - baseline_value) / baseline_value) * 100
            return formatted_value, f"{delta:+.1f}%", "normal"
        return formatted_value, None, "off"
    
    return formatted_value, None, "off"


def render_metrics_grid(metric_data: dict, display_name: str, comparison_type: str = "Value"):
    """
    Render a grid of metrics using Streamlit's metric component.
    
    Parameters:
    metric_data (dict): Dictionary containing DataFrames for each metric
    display_name (str): Name of the selected geographic area
    comparison_type (str): Type of comparison to show
    """
    cols = st.columns(2)
    col_idx = 0
    
    for metric, title in METRICS:
        formatted_value, delta, delta_color = create_metrics_view(
            metric_data[metric],
            metric,
            title,
            comparison_type
        )
        
        with cols[col_idx]:
            st.metric(
                label=title,
                value=formatted_value,
                delta=delta,
                delta_color=delta_color
            )
        
        col_idx = (col_idx + 1) % 2


def create_choropleth(
    df: pd.DataFrame,
    geometries: Dict,
    metric: str,
    title: str,
    level: str,
    selected_id: Optional[str] = None,
    comparison_type: str = "Value"
) -> alt.Chart:
    """Create unified choropleth map for all geographic levels"""
    # Get latest data and handle comparisons
    latest_date = df['date'].max()
    df_latest = df[df['date'] == latest_date].copy()
    format_str = ',.0f'
    
    color_scheme = 'yellowgreenblue'

    # Handle comparison calculations
    if comparison_type != "Value":
        # Calculate comparison dates
        prev_date = {
            "MoM": latest_date - pd.DateOffset(months=1),
            "YoY": latest_date - pd.DateOffset(years=1),
            "Since 2019": df[df['date'].dt.year == 2019]['date'].max()
        }.get(comparison_type, None)

        if prev_date is not None:
            df_prev = df[df['date'] == prev_date].copy()

            # Calculate percent changes
            if not df_prev.empty:
                df_latest = df_latest.merge(
                    df_prev[['id', metric]],
                    on='id',
                    suffixes=('', '_prev')
                )
                df_latest[metric] = ((df_latest[metric] - df_latest[f'{metric}_prev']) /
                                     df_latest[f'{metric}_prev'] * 100)
                format_str = '+.1f'

    # Configure geographic parameters
    if level == 'metro':
        # Special handling for metro areas
        # Clean and validate the metric data
        df_latest[metric] = pd.to_numeric(df_latest[metric], errors='coerce')
        valid_data = df_latest[df_latest[metric].notna()]
        
        # Set domain with validation
        min_val = valid_data[metric].min()
        max_val = valid_data[metric].max()
        
        # Handle edge cases
        if pd.isna(min_val) or pd.isna(max_val) or np.isinf(min_val) or np.isinf(max_val):
            st.warning(f"No valid data available for {title}")
            return None
            
        base = alt.Chart(
            alt.Data(values=geometries['metros']['features'])
        ).mark_geoshape(
            stroke='blue',
            strokeWidth=0.5
        ).encode(
            color=alt.Color(
                f'{metric}:Q',
                title=title,
                scale=alt.Scale(
                    scheme=color_scheme,
                    domain=[min_val, max_val]  # Using validated values
                ),
                legend=None
            ),
            tooltip=[
                alt.Tooltip('cbsa_title:N', title='Metro Area'),
                alt.Tooltip(f'{metric}:Q', title=title, format=format_str)
            ]
        ).transform_lookup(
            lookup='id',
            from_=alt.LookupData(valid_data, 'id', [metric, 'cbsa_title'])  # Using validated data
        )

        # Add highlight for selected area if provided
        if selected_id is not None:
            highlight = base.transform_filter(
                f"datum.id === '{selected_id}'"
            ).mark_geoshape(
                stroke='red',
                strokeWidth=2
            )
            base = alt.layer(base, highlight)

        # Add state boundaries for context
        state_borders = alt.Chart(geometries['states']).mark_geoshape(
            stroke='black',
            strokeWidth=1,
            fill=None
        )
        base = alt.layer(base, state_borders)

    else:
        # Configure other geographic levels
        geo_config = {
            'country': {
                'geometry': geometries['countries'],
                'name_field': 'country',
                'domain': get_valid_domain(df_latest, metric)
            },
            'state': {
                'geometry': geometries['states'],
                'name_field': 'state',
                'domain': get_valid_domain(df_latest, metric)
            },
            'county': {
                'geometry': geometries['counties'],
                'name_field': 'county_name',
                'domain': get_valid_domain(df_latest, metric, use_quantiles=True)
            }
        }.get(level, None)

        if geo_config is None:
            raise ValueError(f"Invalid geographic level: {level}")

        # Create base map
        base = alt.Chart(geo_config['geometry']).mark_geoshape(
            stroke='black',
            strokeWidth=1
        ).encode(
            color=alt.Color(
                f'{metric}:Q',
                title=title,
                scale=alt.Scale(
                    scheme=color_scheme,
                    domain=geo_config['domain']
                ),
                legend=None
            ),
            tooltip=[
                alt.Tooltip(f"{geo_config['name_field']}:N", title='Area'),
                alt.Tooltip(f'{metric}:Q', title=title, format=format_str)
            ]
        ).transform_lookup(
            lookup='id',
            from_=alt.LookupData(df_latest, 'id', [metric, geo_config['name_field']])
        )

        # Add highlight for selected area
        # Add highlight for selected area
        if selected_id is not None:
            highlight_stroke_width = 0.5 if level == 'country' else 3
            highlight = base.transform_filter(
                f"datum.id === {selected_id}"
            ).mark_geoshape(
                stroke='red',
                strokeWidth=highlight_stroke_width
            )
            base = alt.layer(base, highlight)

        # Add label for country map
        if level == 'country':
            label_data = df_latest[['id', metric, geo_config['name_field']]].copy()
            label_data['lat'] = 40  # Approximate center latitude for the US
            label_data['lon'] = -98  # Approximate center longitude for the US

            label = alt.Chart(label_data).mark_text(
                align='center',
                baseline='middle',
                fontSize=24,
                fontWeight='bold',
                color='white'
            ).encode(
                text=alt.Text(f'{metric}:Q', format=format_str)
            )
            base = alt.layer(base, label)

    # Add projection and properties
    return base.project(
        type='albersUsa'
    ).properties(
        width=500,
        height=300,
        title={
            "text": f"{title} ({comparison_type})" if comparison_type != "Value" else title,
            "fontSize": 16,
            "anchor": "start"
        }
    )


def handle_map_visualization(
    geo_level: str,
    selected_area: Optional[str] = None,
    selected_id: Optional[str] = None,
    comparison_type: str = "Value"
) -> None:
    """Unified map visualization handler with improved error handling"""
    try:
        data_loader = st.session_state.data_loader
        df = data_loader.load_data(geo_level)
        geometries = load_geometries()
        
        if geometries is None:
            st.error("Failed to load map geometries")
            return
            
        # Create metrics in pairs using list comprehension
        metric_pairs = [(METRICS[i], METRICS[i+1]) if i+1 < len(METRICS) else (METRICS[i], None) 
                       for i in range(0, len(METRICS), 2)]
        
        for metric_pair in metric_pairs:
            col1, col2 = st.columns(2, gap="small")
            
            for metric_info, col in zip(metric_pair, [col1, col2]):
                if metric_info is None:
                    continue
                    
                metric, title = metric_info
                with col:
                    chart = create_choropleth(df, geometries, metric, title,
                                           geo_level, selected_id, comparison_type)
                    if chart:
                        st.altair_chart(chart, use_container_width=True)

    except Exception as e:
        st.error(f"Error in map visualization: {str(e)}")

def render_overview():
    """Main overview rendering function"""
    # Get DataLoader instance
    data_loader = st.session_state.data_loader
    
    selected_geo_level = st.radio(
        "Geographic Level",
        options=["Country", "State", "Metro", "County", "Zip"],
        horizontal=True,
        label_visibility="collapsed"
    ).lower()
    
    col1, col2, col3 = st.columns([3, 3, 5], gap="small")

    with col1:
        # Load data using DataLoader
        df = data_loader.load_data(selected_geo_level)
        available_geos = data_loader.get_available_geos(selected_geo_level)
        
        if selected_geo_level == 'country':
            selected_geo = st.selectbox(
                'Select Country',
                options=['United States'],
                disabled=True
            )
            selected_id = data_loader.COUNTRY_MAPPING['United States']
            selected_geo = (str(selected_id), "United States")
            display_name = "United States"
        else:
            if not available_geos:
                st.error(f"No data available for {selected_geo_level}")
                return
                
            selected_geo = st.selectbox(
                f"Select {data_loader.GEO_MAPPINGS[selected_geo_level.title()]['display_name']}",
                options=available_geos,
                format_func=lambda x: x[1]
            )
            display_name = selected_geo[1]
            selected_id = selected_geo[0]
    
    with col2:
        chart_type = st.selectbox(
            "Chart Type",
            options=["Time Series", "Seasonality", "Metrics", "Map"]
        )
    
    with col3:
        comparison_options = ["Value"] if chart_type == "Seasonality" else ["Value", "MoM", "YoY", "Since 2019"]
        comparison_type = st.segmented_control(
            "Comparison",
            options=comparison_options,
            default="Value"
        )

    try:
        if chart_type == "Map":
            if selected_geo_level == 'zip':
                display_coming_soon()
                return
            handle_map_visualization(
                selected_geo_level,
                display_name,
                selected_id,
                comparison_type
            )
            return

        # Load data for other chart types using DataLoader
        metric_data = {}
        for metric, _ in METRICS:
            data = data_loader.get_metric_data(
                selected_geo_level,
                [selected_id],
                metric
            )
            if len(data) == 0:
                st.error(f"No data available for {display_name}")
                return
            metric_data[metric] = data

        # Handle metrics view
        if chart_type == "Metrics":
            st.write(f"#### Current Metrics for {display_name}")
            render_metrics_grid(
                metric_data, 
                display_name, 
                comparison_type
            )
            st.markdown("---")
            return

        # Render regular charts
        for i in range(0, len(METRICS), 2):
            col1, col2 = st.columns(2, gap="small")
            
            # First chart
            metric, title = METRICS[i]
            with col1:
                if chart_type == "Time Series":
                    if comparison_type == "Value":
                        chart = create_area_chart(metric_data[metric], metric, title, display_name)
                    else:
                        chart = create_combo_chart(metric_data[metric], metric, title, display_name, comparison_type)
                elif chart_type == "Seasonality":
                    chart = create_seasonality_chart(metric_data[metric], metric, title, display_name)
                st.altair_chart(chart, use_container_width=True)
            
            # Second chart
            if i + 1 < len(METRICS):
                metric, title = METRICS[i + 1]
                with col2:
                    if chart_type == "Time Series":
                        if comparison_type == "Value":
                            chart = create_area_chart(metric_data[metric], metric, title, display_name)
                        else:
                            chart = create_combo_chart(metric_data[metric], metric, title, display_name, comparison_type)
                    elif chart_type == "Seasonality":
                        chart = create_seasonality_chart(metric_data[metric], metric, title, display_name)
                    st.altair_chart(chart, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading visualizations: {str(e)}")
        return

def get_valid_domain(data: pd.DataFrame, metric: str, use_quantiles: bool = False) -> List[float]:
    """Get valid domain values for the color scale"""
    # Convert to numeric and drop NA/infinite values
    valid_data = pd.to_numeric(data[metric], errors='coerce')
    valid_data = valid_data[valid_data.notna() & ~np.isinf(valid_data)]
    
    if valid_data.empty:
        return [0, 1]  # Default domain if no valid data
        
    if use_quantiles:
        min_val = valid_data.quantile(0.1)
        max_val = valid_data.quantile(0.9)
    else:
        min_val = valid_data.min()
        max_val = valid_data.max()
    
    # Ensure we don't have identical min/max
    if min_val == max_val:
        if min_val == 0:
            max_val = 1
        else:
            min_val = max_val * 0.9
            
    return [min_val, max_val]

def validate_metric_data(df: pd.DataFrame, metric: str) -> Tuple[pd.DataFrame, Optional[str]]:
    """Validate metric data and return cleaned dataframe and error message if any"""
    try:
        df[metric] = pd.to_numeric(df[metric], errors='coerce')
        valid_data = df[df[metric].notna()]
        
        if valid_data.empty:
            return None, f"No valid data available for {metric}"
            
        if valid_data[metric].isin([np.inf, -np.inf]).any():
            return None, f"Invalid values found in {metric}"
            
        return valid_data, None
    except Exception as e:
        return None, f"Error processing {metric}: {str(e)}"
