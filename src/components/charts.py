import altair as alt
import pandas as pd
from src.data.data_loader import METRICS

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

def get_axis_config(df: pd.DataFrame) -> dict:
    """
    Return appropriate axis configuration based on date range in the data.
    """
    # Calculate the date range in days
    date_range = (df['date'].max() - df['date'].min()).days
    
    # For periods less than or equal to 1 year (365 days)
    if date_range <= 366:
        return {
            "format": "%b",  # Abbreviated month name (Jan, Feb, etc.)
            "labelAngle": 0,
            "tickCount": "month"  # Show all months
        }
    # For periods greater than 1 year
    else:
        return {
            "format": "%Y",  # Year only (2023, 2024, etc.)
            "labelAngle": 0,
            "tickCount": "year"  # Show all years
        }

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

    # Get axis configuration based on date range
    axis_config = get_axis_config(df)
    
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
            axis=alt.Axis(**axis_config)
        ),
        y=alt.Y(
            f'{metric}:Q',
            title=None,
            scale=alt.Scale(zero=False),
            axis=alt.Axis(format='~s')
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
    df = df.copy().sort_values('date')  # Ensure data is sorted by date
    
    # Calculate comparison values based on type
    if comparison_type == "MoM":
        # First sort by date and then calculate the change
        df['previous'] = df[metric].shift(1)
        df['comparison'] = df.apply(
            lambda row: ((row[metric] - row['previous']) / row['previous'] * 100) 
            if pd.notnull(row['previous']) else None, 
            axis=1
        )
        comparison_label = "MoM Change (%)"
    elif comparison_type == "YoY":
        df['previous'] = df[metric].shift(12)
        df['comparison'] = df.apply(
            lambda row: ((row[metric] - row['previous']) / row['previous'] * 100)
            if pd.notnull(row['previous']) else None,
            axis=1
        )
        comparison_label = "YoY Change (%)"
    elif comparison_type == "Since 2019":
        baseline_2019 = df[df['date'].dt.year == 2019].copy()
        baseline_2019['month'] = baseline_2019['date'].dt.month
        df['month'] = df['date'].dt.month
        df = df.merge(
            baseline_2019[['month', metric]], 
            on='month', 
            suffixes=('', '_2019')
        )
        df['comparison'] = ((df[metric] - df[f'{metric}_2019']) / df[f'{metric}_2019']) * 100
        comparison_label = "Change Since 2019 (%)"
    
    # Drop the temporary columns if they exist
    if 'previous' in df.columns:
        df = df.drop('previous', axis=1)
    
    # Selection for hover interaction
    nearest = alt.selection_single(
        nearest=True,
        on='mouseover',
        fields=['date'],
        empty='none',
        clear='mouseout'
    )
    
    # Get axis configuration based on date range
    axis_config = get_axis_config(df)
    
    # Base chart
    base = alt.Chart(df).encode(
        x=alt.X(
            'date:T', 
            title=None,
            axis=alt.Axis(
                grid=False,
                **axis_config
            )
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
                ticks=False,
                orient='left'
            )
        )
    )
    
    # Comparison bars
    bars = base.mark_bar(opacity=0.3, width=2.5).encode(
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

def calculate_change(df, metric_col, change_type):
    """Calculate percentage change based on the selected view"""
    df = df.copy()
    
    if change_type == 'MoM':  # Month over Month
        df[metric_col] = df[metric_col].pct_change(periods=1) * 100
    elif change_type == 'YoY':  # Year over Year
        df[metric_col] = df[metric_col].pct_change(periods=12) * 100
    elif change_type == 'Since 2019':
        # Get the 2019 average value
        baseline = df[df['date'].dt.year == 2019][metric_col].mean()
        df[metric_col] = ((df[metric_col] - baseline) / baseline) * 100
        
    return df

def create_line_chart(dfs, metric_col, metric_name, display_names, selected_period, view_type):
    """Create a line chart comparing multiple locations"""
    import altair as alt
    
    # Combine all dataframes with a location identifier
    chart_data = []
    for df, name in zip(dfs, display_names):
        temp_df = df[['date', metric_col]].copy()
        
        # Apply percentage change calculations if not 'Value' view
        if view_type != 'Value':
            temp_df = calculate_change(temp_df, metric_col, view_type)
            
        temp_df['Location'] = name
        chart_data.append(temp_df)
    
    chart_df = pd.concat(chart_data)
    
    # Get date range for subtitle
    start_date = chart_df['date'].min().strftime('%B %Y')
    end_date = chart_df['date'].max().strftime('%B %Y')
    
    # Determine date format based on selected period
    if selected_period in ['3M', '6M', 'YTD', '1Y']:
        date_format = "%b"  # Jan, Feb, Mar format
        tick_count = 'month'
    else:  # '5Y' or 'Max'
        date_format = "%Y"  # YYYY format
        tick_count = 'year'
    
    # Prepare tooltip data by pivoting
    tooltip_data = chart_df.pivot(
        index='date',
        columns='Location',
        values=metric_col
    ).reset_index()
    
    # Define color scale for consistent colors
    color_scale = alt.Scale(
        domain=display_names
    )
    
    # Add formatted columns for each location
    if view_type != 'Value':
        for location in display_names:
            tooltip_data[f'{location}_formatted'] = tooltip_data[location].apply(lambda x: f'{x:+.1f}%')
    else:
        format_str = get_metric_format(metric_col)
        for location in display_names:
            if format_str.startswith('$'):
                tooltip_data[f'{location}_formatted'] = tooltip_data[location].apply(lambda x: f'${x:,.0f}')
            elif 'ratio' in metric_col:
                tooltip_data[f'{location}_formatted'] = tooltip_data[location].apply(lambda x: f'{x:.2f}')
            else:
                tooltip_data[f'{location}_formatted'] = tooltip_data[location].apply(lambda x: f'{x:,.0f}')
    
    # Create selection for hover
    nearest = alt.selection_single(
        nearest=True,
        on='mouseover',
        fields=['date'],
        empty='none'
    )
    
    # Update y-axis format based on view type
    y_format = '~s' if view_type == 'Value' else '+.1f'
    y_title = '' if view_type == 'Value' else '% Change'
    
    # Create the base chart with proper mark_line() configuration
    chart = alt.Chart(chart_df).mark_line(
        interpolate='linear',  # Use linear interpolation for smooth lines
        point=False  # Disable points unless you specifically want them
    ).encode(
        x=alt.X('date:T', 
                title=None,
                axis=alt.Axis(
                    labelAngle=0,
                    labelFontSize=11,
                    format=date_format,
                    tickCount=tick_count,
                    domain=True
                )),
        y=alt.Y(
            f'{metric_col}:Q',
            title=y_title,
            scale=alt.Scale(zero=True if view_type != 'Value' else False),
            axis=alt.Axis(
                labelFontSize=11,
                format=y_format,
                domain=True
            )
        ),
        color=alt.Color('Location:N', 
                       scale=color_scale,
                       title=None,
                       legend=alt.Legend(
                           orient='top-right',
                           labelFontSize=11,
                           symbolSize=50,
                           direction='vertical',
                           padding=10,
                           offset=0,
                           labelLimit=200,
                           columns=1,
                           labelAlign='right',
                           symbolLimit=50,
                           rowPadding=5,
                           labelOffset=10
                       ))
    )

    # Points on the lines
    points = chart.mark_point(size=100).encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    # Create tooltips for all locations
    tooltips = [alt.Tooltip('date:T', title='Date', format='%B %Y')]
    for location in display_names:
        tooltips.append(
            alt.Tooltip(
                f'{location}_formatted:N',
                title=location
            )
        )

    # Vertical rule at the hover point
    rule = alt.Chart(tooltip_data).mark_rule(color='gray').encode(
        x='date:T',
        opacity=alt.condition(nearest, alt.value(0.3), alt.value(0)),
        tooltip=tooltips
    ).add_selection(nearest)

    # Combine the layers
    chart = alt.layer(
        chart, points, rule
    ).properties(
        height=300,
        width='container',
        title={
            "text": f"{metric_name}",
            "subtitle": [
                f"Comparing {len(display_names)} Locations from {start_date} - {end_date}"
            ],
            "color": "black",
            "subtitleColor": "gray",
            "fontSize": 16,
            "subtitleFontSize": 12,
            "anchor": "start",
            "offset": 20
        }
    ).configure_axis(
        grid=True,
        gridOpacity=0.2
    ).configure_view(
        stroke=None
    )
    
    return chart
