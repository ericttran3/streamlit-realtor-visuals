import streamlit as st
import streamlit_shadcn_ui as ui
import pandas as pd
from src.data.data_loader import METRICS

def create_comparison_table(df: pd.DataFrame, display_name: str, comparison_type: str) -> None:
    """Create a detailed comparison table showing metrics and their changes."""
    # Get latest date
    latest_date = df['date'].max()
    
    # Use METRICS dictionary instead of hardcoded list
    metrics = list(METRICS.items())
    
    rows = []
    for metric_col, metric_name in metrics:
        try:
            # Get latest value
            latest_value = df[df['date'] == latest_date][metric_col].iloc[0]
            
            # Format the current value based on metric type
            if 'price' in metric_col:
                formatted_latest = f"${latest_value:,.0f}"
            else:
                formatted_latest = f"{latest_value:,.0f}"
            
            row = {"Metric": metric_name}
            
            if comparison_type == "Value":
                row[f"{latest_date.strftime('%B %Y')}"] = formatted_latest
            
            elif comparison_type == "Seasonality":
                # Get current month
                current_month = latest_date.month
                
                # Get historical values for the same month (excluding current year)
                historical_data = df[
                    (df['date'].dt.month == current_month) & 
                    (df['date'].dt.year < latest_date.year)
                ][metric_col]
                
                if not historical_data.empty:
                    historical_avg = historical_data.mean()
                    raw_delta = latest_value - historical_avg
                    pct_change = ((latest_value - historical_avg) / historical_avg) * 100
                    
                    if 'price' in metric_col:
                        formatted_avg = f"${historical_avg:,.0f}"
                        formatted_delta = f"{'+' if raw_delta > 0 else '-'}${abs(raw_delta):,.0f}"
                    else:
                        formatted_avg = f"{historical_avg:,.0f}"
                        formatted_delta = f"{raw_delta:+,.0f}"
                    
                    row.update({
                        f"{latest_date.strftime('%B %Y')}": formatted_latest,
                        f"Historical {latest_date.strftime('%B')} Average": formatted_avg,
                        "Change": formatted_delta,
                        "Change (%)": f"{pct_change:+.1f}%"
                    })
                
            else:  # MoM, YoY, Since 2019
                if comparison_type == "MoM":
                    prev_date = latest_date - pd.DateOffset(months=1)
                elif comparison_type == "YoY":
                    prev_date = latest_date - pd.DateOffset(years=1)
                elif comparison_type == "Since 2019":
                    prev_date = pd.Timestamp(year=2019, month=latest_date.month, day=1)
                
                prev_date = df['date'].where(df['date'] <= prev_date).max()
                
                if prev_date is not None:
                    prev_value = df[df['date'] == prev_date][metric_col].iloc[0]
                    raw_delta = latest_value - prev_value
                    pct_change = ((latest_value - prev_value) / prev_value) * 100
                    
                    if 'price' in metric_col:
                        formatted_prev = f"${prev_value:,.0f}"
                        formatted_delta = f"{'+' if raw_delta > 0 else '-'}${abs(raw_delta):,.0f}"
                    else:
                        formatted_prev = f"{prev_value:,.0f}"
                        formatted_delta = f"{raw_delta:+,.0f}"
                    
                    row.update({
                        f"{latest_date.strftime('%B %Y')}": formatted_latest,
                        f"{prev_date.strftime('%B %Y')}": formatted_prev,
                        "Change": formatted_delta,
                        "Change (%)": f"{pct_change:+.1f}%"
                    })
                
            rows.append(row)
            
        except Exception as e:
            st.error(f"Error processing {metric_name}: {str(e)}")
    
    # Create DataFrame and display table
    if rows:
        df_table = pd.DataFrame(rows)
        ui.table(
            data=df_table,
            maxHeight=400
        )
        
        # Create caption
        geo_level = (
            "County" if ", " in display_name
            else "Metro Area" if "Metro" in display_name or "MSA" in display_name
            else "State" if len(display_name) == 2
            else "Country" if display_name == "United States"
            else "Location"
        )
        
        # caption = (
        #     f"Table displaying the {comparison_type} comparison for {display_name} "
        #     f"at the {geo_level} level as of {latest_date.strftime('%B %Y')}"
        # )
        st.caption("Adjust the views in Filters to update the table for month-over-month or year-over-year comparisons.")

def create_comparison_matrix(dfs: list, display_names: list) -> None:
    """Create a matrix table comparing metrics across locations."""
    # Get latest date
    latest_date = max(df['date'].max() for df in dfs)
    
    # Use METRICS dictionary
    metrics = list(METRICS.items())
    
    rows = []
    for metric_col, metric_name in metrics:
        try:
            row = {"Metric": metric_name}
            
            # Add values for each location
            for df, name in zip(dfs, display_names):
                latest_value = df[df['date'] == latest_date][metric_col].iloc[0]
                
                # Format the value based on metric type
                if 'price' in metric_col:
                    formatted_value = f"${latest_value:,.0f}"
                elif 'ratio' in metric_col:
                    formatted_value = f"{latest_value:.2f}"
                else:
                    formatted_value = f"{latest_value:,.0f}"
                
                row[name] = formatted_value
            
            rows.append(row)
            
        except Exception as e:
            st.error(f"Error processing {metric_name}: {str(e)}")
    
    # Create DataFrame and display table
    if rows:
        df_table = pd.DataFrame(rows)
        ui.table(
            data=df_table,
            maxHeight=400
        )
        
        st.caption(f"Values as of {latest_date.strftime('%B %Y')}")
