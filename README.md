# Streamlit Realtor.com Data Visualizer

## Overview
An interactive data visualization application built with Streamlit that provides insights into real estate market trends using publicly available data from realtor.com/research/data. The app aggregates and visualizes data across multiple geographic levels including national, state, metro, county, and ZIP code regions.

## Features

### 📊 Data Visualization
- Interactive time series charts using Altair
- Comparative analysis across different geographic regions
- Seasonal trend analysis
- Multiple view options:
  - Raw values
  - Month-over-Month (MoM) changes
  - Year-over-Year (YoY) changes
  - Changes since 2019
  - Seasonality patterns

## Technology Stack

### Core Technologies
- Python
- Streamlit
- Altair
- Folium
- Pandas
- Dask (for large dataset handling)

### Enhanced UI Components
- streamlit_shadcn_ui
- streamlit_searchbox
- streamlit-antd-components
- streamlit-folium

## Installation

1. Clone the repository:
```
bash
git clone https://github.com/yourusername/streamlit-realtor-visuals.git
cd streamlit-realtor-visuals
```

2. Install the required packages:
```
pip install -r requirements.txt
```

3. Run the app:
```
streamlit run app.py
```

## Upcoming Features
- Enhanced interactive mapping capabilities using Folium
- ChatAI integration for natural language data queries
- Additional visualization options
- Mobile-responsive design improvements

## Data Source
All data is sourced from [realtor.com/research/data](https://realtor.com/research/data), providing comprehensive real estate market metrics including:
- Median listing prices
- Active listing counts
- Days on market
- New listings
- Price changes
- Pending sales
- Price per square foot
- And more...

## Contributing
Feedback, bug reports, and contributions are welcome! Please feel free to:
- Submit issues for bug reports or feature requests
- Create pull requests for improvements
- Share suggestions for enhancing the user experience

## Contact
For questions, feedback, or bug reports, please contact:
- Email: ericttran3@gmail.com
- LinkedIn: [Eric Tran](https://www.linkedin.com/in/ericttran3/)
- GitHub Issues: [Create an issue](https://github.com/yourusername/streamlit-realtor-visuals/issues)

## License
This project is licensed under the MIT License - see the LICENSE file for details.
