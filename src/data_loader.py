from typing import Dict, List, Tuple, Optional
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

class DataLoader:
    def __init__(self):
        self.data_cache: Dict[str, pd.DataFrame] = {}
        
        # Define mappings
        self.COUNTRY_MAPPING = {'United States': 840}
        
        self.STATE_FIPS = {
            'Alabama': 1, 'Alaska': 2, 'Arizona': 4, 'Arkansas': 5, 'California': 6,
            'Colorado': 8, 'Connecticut': 9, 'Delaware': 10, 'District of Columbia': 11,
            'Florida': 12, 'Georgia': 13, 'Hawaii': 15, 'Idaho': 16, 'Illinois': 17,
            'Indiana': 18, 'Iowa': 19, 'Kansas': 20, 'Kentucky': 21, 'Louisiana': 22,
            'Maine': 23, 'Maryland': 24, 'Massachusetts': 25, 'Michigan': 26,
            'Minnesota': 27, 'Mississippi': 28, 'Missouri': 29, 'Montana': 30,
            'Nebraska': 31, 'Nevada': 32, 'New Hampshire': 33, 'New Jersey': 34,
            'New Mexico': 35, 'New York': 36, 'North Carolina': 37, 'North Dakota': 38,
            'Ohio': 39, 'Oklahoma': 40, 'Oregon': 41, 'Pennsylvania': 42,
            'Rhode Island': 44, 'South Carolina': 45, 'South Dakota': 46,
            'Tennessee': 47, 'Texas': 48, 'Utah': 49, 'Vermont': 50, 'Virginia': 51,
            'Washington': 53, 'West Virginia': 54, 'Wisconsin': 55, 'Wyoming': 56
        }
        
        self.GEO_MAPPINGS = {
            "Country": {
                "id_col": None,
                "name_col": "country",
                "display_name": "Country"
            },
            "State": {
                "id_col": "state_id",
                "name_col": "state",
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
        
        # Define data file paths
        self.DATA_FILES = {
            'country': 'data/realtor/RDC_Inventory_Core_Metrics_Country_History.csv',
            'state': 'data/realtor/RDC_Inventory_Core_Metrics_State_History.csv',
            'metro': 'data/realtor/RDC_Inventory_Core_Metrics_Metro_History.csv',
            'county': 'data/realtor/RDC_Inventory_Core_Metrics_County_History.csv',
            'zip': 'data/realtor/RDC_Inventory_Core_Metrics_Zip_History.csv'
        }
        
        # Define the columns we need for all geographic levels
        self.base_columns = [
            'month_date_yyyymm',
            'median_listing_price',
            'active_listing_count',
            'median_days_on_market',
            'new_listing_count',
            'price_increased_count',
            'price_reduced_count',
            'pending_listing_count',
            'median_listing_price_per_square_foot',
            'median_square_feet',
            'average_listing_price',
            'total_listing_count',
            'pending_ratio'
        ]

    def load_data(self, geo_level: str) -> pd.DataFrame:
        """Load and cache data for a specific geographic level"""
        geo_level = geo_level.lower()
        
        if geo_level not in self.data_cache:
            try:
                df = pd.read_csv(self.DATA_FILES[geo_level])
                
                # Add ID column based on geographic level
                if geo_level == 'country':
                    df['id'] = df['country'].map(self.COUNTRY_MAPPING)
                elif geo_level == 'state':
                    df['id'] = df['state'].map(self.STATE_FIPS)
                elif geo_level == 'county':
                    df['id'] = df['county_fips'].astype(int)
                    # Format existing county_name: capitalize county and uppercase state code
                    df['county_name'] = df['county_name'].apply(
                        lambda x: f"{x.split(',')[0].title()}, {x.split(',')[1].strip().upper()}"
                    )
                elif geo_level == 'zip':
                    df['id'] = df['postal_code'].astype(str)
                elif geo_level == 'metro':
                    df['id'] = df['cbsa_code'].astype(str)
                    df['cbsa_title'] = df['cbsa_title'].astype(str)
                
                # Convert date column
                df['date'] = pd.to_datetime(df['month_date_yyyymm'].astype(str), format='%Y%m')
                
                # Cache the data
                self.data_cache[geo_level] = df
                
            except Exception as e:
                raise Exception(f"Error loading {geo_level} data: {str(e)}")
        
        return self.data_cache[geo_level]

    def get_metric_data(self, 
                       geo_level: str, 
                       geo_ids: List[str], 
                       metric: str,
                       start_date: Optional[str] = None) -> pd.DataFrame:
        """Get formatted metric data ready for visualization."""
        geo_level = geo_level.lower()
        
        if not geo_ids:
            return pd.DataFrame()
        
        # Load data for each geo_id
        dfs = []
        for geo_id in geo_ids:
            df = self.load_data(geo_level)
            df = df[df['id'].astype(str) == str(geo_id)].copy()
            
            # Apply date filter if provided
            if start_date:
                df = df[df['date'] >= pd.to_datetime(start_date)]
            
            if len(df) > 0:
                viz_df = df[['date', metric]].copy()
                viz_df['geo_id'] = str(geo_id)
                viz_df['geo_name'] = df.iloc[0].get(self.GEO_MAPPINGS[geo_level.title()]['name_col'])
                dfs.append(viz_df)
        
        # Combine all data
        if dfs:
            return pd.concat(dfs, ignore_index=True)
        return pd.DataFrame()

    def get_available_geos(self, geo_level: str) -> List[Tuple[str, str]]:
        """Get list of available geographic entities."""
        geo_level = geo_level.title()
        
        if geo_level == "Country":
            return [('840', 'United States')]
            
        df = self.load_data(geo_level.lower())
        mapping = self.GEO_MAPPINGS[geo_level]
        id_col = 'id'  # We now use our standardized 'id' column
        name_col = mapping['name_col']
        
        # Get unique geos
        unique_geos = df[[id_col, name_col]].drop_duplicates()
        
        # Format the results
        valid_geos = []
        for _, row in unique_geos.iterrows():
            geo_id = str(row[id_col])
            if geo_level == "Zip":
                valid_geos.append((
                    geo_id,
                    f"{geo_id} - {row[name_col]}"
                ))
            else:
                valid_geos.append((geo_id, str(row[name_col])))
        
        # Sort by name
        valid_geos.sort(key=lambda x: x[1])
        
        return valid_geos
