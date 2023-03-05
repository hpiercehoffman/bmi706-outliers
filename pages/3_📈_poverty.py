import altair as alt
import pandas as pd
import streamlit as st
from vega_datasets import data

import process_data

# Configure how the page appears in browser tab
st.set_page_config(page_title="2014 Poverty Rates", page_icon="📈")

# @st.cache_data

def collect_poverty_data():
    poverty_df = process_data.read_poverty_csv()
    poverty_df = poverty_df.rename({'Poverty Percent, All Ages': 'percent',
                                    'County FIPS Code': 'id'},
                                    axis='columns')
    return poverty_df

poverty_df = collect_poverty_data()

st.write("2014 poverty rates")

# Map of the U.S. by counties
counties = alt.topo_feature(data.us_10m.url, 'counties')

st.dataframe(poverty_df)
