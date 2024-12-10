import streamlit as st
import streamlit_shadcn_ui as ui
import pandas as pd
from src.data.data_loader import METRICS

def create_metrics_grid(df: pd.DataFrame, display_name: str, comparison_type: str = "Value"):
    """
    Render metrics in a grid layout with cards showing values and comparisons.
    Maximum 4 columns per row.
    """
    # Get latest date
    latest_date = df['date'].max()
    
    # Use METRICS dictionary instead of hardcoded list
    metrics = list(METRICS.items())
    
    # Split metrics into rows of 4
    for i in range(0, len(metrics), 4):
        # Get the next 4 metrics (or fewer for the last row)
        row_metrics = metrics[i:i+4]
        
        # Create columns for this row
        cols = st.columns(4)
        
        # Render metrics in columns
        for (metric, title), col in zip(row_metrics, cols):
            with col:
                try:
                    # Get the latest value
                    latest_value = df[df['date'] == latest_date][metric].iloc[0]
                    
                    # Calculate delta based on comparison type
                    delta = None
                    if comparison_type == "Seasonality":
                        # Get current month
                        current_month = latest_date.month
                        
                        # Get historical values for the same month (excluding current year)
                        historical_data = df[
                            (df['date'].dt.month == current_month) & 
                            (df['date'].dt.year < latest_date.year)
                        ][metric]
                        
                        if not historical_data.empty:
                            # Calculate average of historical values
                            historical_avg = historical_data.mean()
                            # Calculate percentage difference
                            delta = ((latest_value - historical_avg) / historical_avg) * 100
                            description = (
                                f"from {latest_date.strftime('%B')} average"
                            )
                        else:
                            description = "no historical data available"
                    
                    elif comparison_type == "MoM":
                        prev_date = latest_date - pd.DateOffset(months=1)
                        prev_date = df['date'].where(df['date'] <= prev_date).max()
                        if prev_date:
                            prev_value = df[df['date'] == prev_date][metric].iloc[0]
                            delta = ((latest_value - prev_value) / prev_value) * 100
                            description = "from last month"
                        else:
                            description = "no prior data"
                    
                    elif comparison_type == "YoY":
                        year_ago_date = latest_date - pd.DateOffset(years=1)
                        year_ago_date = df['date'].where(df['date'] <= year_ago_date).max()
                        if year_ago_date:
                            year_ago_value = df[df['date'] == year_ago_date][metric].iloc[0]
                            delta = ((latest_value - year_ago_value) / year_ago_value) * 100
                            description = "from last year"
                        else:
                            description = "no prior data"
                    
                    elif comparison_type == "Since 2019":
                        baseline_2019 = df[df['date'].dt.year == 2019]
                        if not baseline_2019.empty:
                            current_month = latest_date.month
                            baseline_value = baseline_2019[
                                baseline_2019['date'].dt.month == current_month
                            ][metric].iloc[0]
                            delta = ((latest_value - baseline_value) / baseline_value) * 100
                            description = f"since {latest_date.strftime('%B')} 2019"
                        else:
                            description = "no 2019 data"
                    else:  # Value
                        description = f"as of {latest_date.strftime('%B %Y')}"

                    # Format the value based on metric type
                    if 'price' in metric:
                        formatted_value = f"${latest_value:,.0f}"
                    elif 'ratio' in metric:
                        formatted_value = f"{latest_value:.2f}"
                    else:
                        formatted_value = f"{latest_value:,.0f}"
                    
                    # Add delta to description if available
                    if comparison_type != "Value" and delta is not None:
                        description = f"{delta:+.1f}% {description}"
                    
                    # Create a unique key using display_name, metric, and comparison_type
                    unique_key = f"{display_name}_{metric}_{comparison_type}".lower().replace(" ", "_")
                    
                    # Render the card using ui.card with unique key
                    ui.card(
                        title=title,
                        content=formatted_value,
                        description=description,
                        key=unique_key
                    ).render()
                    
                except Exception as e:
                    st.error(f"Error displaying metric {title}: {str(e)}")
