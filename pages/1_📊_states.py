import altair as alt
import pandas as pd
import streamlit as st
from vega_datasets import data
from streamlit_vega_lite import altair_component

import process_data

# Configure how the page appears in browser tab
st.set_page_config(page_title="U.S. Mortality", page_icon="📊")

# Cache state data from CSV files, dropping entries without a FIPS code
@st.cache_data
def collect_state_data():
    state_df = process_data.read_states()
    state_df = state_df.dropna(subset=['FIPS'])
    state_df["id"] = state_df["FIPS"].astype(int)
    return state_df

state_df = collect_state_data()

# Additional processing to filter the dataframe for only states, not counties
state_df["str_id"] = state_df["id"].astype(str)
msk = state_df['str_id'].str.len() <= 2
only_state_df = state_df.loc[msk] 
state_to_id = {v:i for (v,i) in zip(only_state_df.State, only_state_df.id) }
id_to_state = {v: k for k, v in state_to_id.items()}

# Sidebar for data filtering widgets
with st.sidebar:
    # Multi-select widget for mortality causes
    display_cause = st.selectbox(
        label="Select a mortality cause",
        options=state_df["cause_name"].unique(),
        index=0
    )

    # Radio buttons to select sex
    display_sex = st.radio(
        label="Select a sex to display",
        options=("Male", "Female", "Both"),
        index=0
    )

    # Slider widget to select year
    display_year = st.slider(
        label="Select a year",
        min_value=1980,
        max_value=2014,
        value=1990
    )

st.title("State and county level mortality rates")

# Subset the dataframe to display only selected categories
subset_df = state_df[state_df.cause_name == display_cause]
subset_df = subset_df[subset_df.sex == display_sex]
subset_df = subset_df[subset_df.year_id == display_year]

# Map of the U.S. by counties
counties = alt.topo_feature(data.us_10m.url, 'counties')

# Main map showing the whole U.S. colored by mortality rate
@st.cache
def country_map():
    selection = alt.selection_single(fields=['id'], empty="none")
    return (alt.Chart(counties).mark_geoshape(
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(data=subset_df, key='id', fields=['mx', 'location_name'])
    ).encode(
        color=alt.condition(selection, alt.value('red'), "mx:Q"),
        tooltip=[alt.Tooltip('location_name:N', title='County Name'),
                 alt.Tooltip('mx:Q', title='Deaths per 100,000', format='.2f')]
    ).project(
        "albersUsa"
    ).add_selection(selection
    ).properties(
        width=650,
        height=300
    ))
    
st.write("Select a county to see its state view")
# Altair component creation so we can do event monitoring for mouse clicks
fips = altair_component(altair_chart=country_map()).get("id")
if fips:
    state_fips = int(fips[0]/1000)|0
    st.write(f"Mortality rates for {id_to_state[state_fips]} ")
    county_fips = fips[0]
    state_mort=alt.Chart(counties).mark_geoshape().transform_calculate(
        state_id = "(datum.id / 1000)|0"
    ).transform_filter(
        (alt.datum.state_id)==state_fips
    ).encode(
        color=alt.Color('mx:Q', title="Deaths per 100,000"),
        stroke=alt.condition(alt.datum.id==fips[0], alt.value('red'), alt.value('white')),
        tooltip=[alt.Tooltip('location_name:N', title='County Name'),
             alt.Tooltip('mx:Q', title='Deaths per 100,000', format='.2f')]
    ).transform_lookup(
        lookup='id', 
        from_=alt.LookupData(data=subset_df , key='id', fields=['mx', 'location_name'])
    ).project("albersUsa").properties(
        width=650,
        height=300
    )
    
    st.altair_chart(state_mort)
    
