import altair as alt
import pandas as pd
import streamlit as st
from vega_datasets import data
from streamlit_vega_lite import altair_component

import process_data

def my_altair_component(altair_chart, key=None):
    import streamlit.components.v1 as components 
    import os
    
    COMPONENT_NAME = "vega_lite_component"
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component(COMPONENT_NAME, path=build_dir)
    
    """Returns selections from the Altair chart.
    Parameters
    ----------
    altair_chart: altair.vegalite.v2.api.Chart
        The Altair chart object to display.
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component"s arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    Returns
    -------
    dict
        The selections from the chart.
    """

    import altair as alt

    # Normally altair_chart.to_dict() would transform the dataframe used by the
    # chart into an array of dictionaries. To avoid that, we install a
    # transformer that replaces datasets with a reference by the object id of
    # the dataframe. We then fill in the dataset manually later on.

    datasets = {}

    # make a copy of the chart so that we don't have to rerender it even if nothing changed
    altair_chart = altair_chart.copy()

    def id_transform(data):
        """Altair data transformer that returns a fake named dataset with the
        object id."""
        name = f"d{id(data)}"
        datasets[name] = data
        return {"name": name}

    alt.data_transformers.register("id", id_transform)

    with alt.data_transformers.enable("id"):
        chart_dict = altair_chart.to_dict()

    return _component_func(spec=chart_dict, **datasets, key=key, default={})


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

# Main chart title


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
                 alt.Tooltip('mx:Q', title='Mortality', format='.2f')]
    ).project(
        "albersUsa"
    ).add_selection(selection
    ).properties(
        width=650,
        height=300
    ))
    
#         color = alt.condition(selection, alt.value('red'), "Deaths per 100,000:Q"),

st.write("Select a county to see its state view")
fips = my_altair_component(altair_chart=country_map()).get("id")
if fips:
    state_fips = int(fips[0]/1000)|0
    st.write(f"Mortality rates for {id_to_state[state_fips]} ")
    county_fips = fips[0]
    state_mort =alt.Chart(counties).mark_geoshape().transform_calculate(
        state_id = "(datum.id / 1000)|0"
    ).transform_filter(
        (alt.datum.state_id)==state_fips
    ).encode(
        color=alt.Color('mx:Q', title="Mortality"),
        tooltip=[alt.Tooltip('location_name:N', title='County Name'),
             alt.Tooltip('mx:Q', title='Mortality', format='.2f')]
    ).transform_lookup(
        lookup='id', 
        from_=alt.LookupData(data=subset_df , key='id', fields=['mx', 'location_name'])
    ).project("albersUsa").properties(
        width=650,
        height=300
    )
    st.altair_chart(state_mort)
    
#     us_mort = alt.Chart(counties).mark_geoshape(
#     ).transform_lookup(
#         lookup='id',
#         from_=alt.LookupData(data=subset_df, key='id', fields=['mx', 'location_name'])
#     ).encode(
#         color=alt.Color('mx:Q', title="Deaths per 100,000"),
#         tooltip=[alt.Tooltip('location_name:N', title='County Name'),
#                  alt.Tooltip('mx:Q', title='Deaths per 100,000', format='.2f')]
#     ).project(
#         "albersUsa"
#     ).properties(
#         width=800,
#         height=400
#     )
    #chart_mort = country_map()


    
# Subset the dataframe to entries belonging to the selected state
# if display_state != 'USA':
#     subset_df_state = subset_df[subset_df.State == display_state]
#     us_scale = alt.Scale(domain=[subset_df_state['mx'].min(), subset_df_state['mx'].max()])
    
#     us_mort = alt.Chart(counties).mark_geoshape(
#     ).transform_lookup(
#         lookup='id',
#         from_=alt.LookupData(data=subset_df, key='id', fields=['mx', 'location_name'])
#     ).transform_calculate(
#         state_id = "(datum.id / 1000)|0"
#     ).encode(
#         color=alt.condition((alt.datum.state_id)==display_state_id, 'mx:Q', alt.value("#808080"), title="Deaths per 100,000", scale=us_scale),
#         tooltip=[alt.Tooltip('location_name:N', title='County Name'),
#                  alt.Tooltip('mx:Q', title='Deaths per 100,000', format='.2f')]
#     ).project(
#         "albersUsa"
#     ).properties(
#         width=500,
#         height=300
#     )
    
#     state_mort =alt.Chart(counties).mark_geoshape().transform_calculate(
#             state_id = "(datum.id / 1000)|0"
#         ).transform_filter(
#             (alt.datum.state_id)==display_state_id
#         ).encode(
#             color=alt.Color('mx:Q', title="Deaths per 100,000", scale=us_scale),
#             tooltip=[alt.Tooltip('location_name:N', title='County Name'),
#                      alt.Tooltip('mx:Q', title='Deaths per 100,000', format='.2f')]
#         ).transform_lookup(
#             lookup='id', 
#             from_=alt.LookupData(data=subset_df_state , key='id', fields=['mx', 'location_name'])
#         ).project("albersUsa").properties(
#             width=600,
#             height=300
#         )
#     chart_mort = alt.vconcat(us_mort, state_mort).resolve_scale(
#         color = 'independent')

# st.altair_chart(chart_mort,
#     use_container_width=False)
