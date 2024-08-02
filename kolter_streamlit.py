import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_js_eval import streamlit_js_eval

# set global variables
base_metro = "Nashville"
current_year = 2024
projected_year = 2029

# set page configurations
st.set_page_config(
    page_title=f"Kolter - {base_metro}",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded" # 'collapsed' or 'expanded'
)

# set Kolter logo
col1, col2, col3 = st.sidebar.columns([0.85,1,1])
col2.image('Data/kolter2.png', width=100)

# sidebar separator
st.sidebar.markdown(
    "<p style='text-align:center;color:#000000;'>---------------</p>", 
    unsafe_allow_html=True
    )

# county select helper text
st.sidebar.markdown(
    f"<p style='text-align:center;color:#000000;'>Select metro {base_metro} county:</p>", 
    unsafe_allow_html=True
    )

# create the sidebar dropdown menu
county_list = {
    '47015': 'Cannon',
    '47021': 'Cheatham',
    '47037': 'Davidson',
    '47043': 'Dickson',
    '47081': 'Hickman',
    '47111': 'Macon',
    '47119': 'Maury',
    '47147': 'Robertson',
    '47149': 'Rutherford',
    '47159': 'Smith',
    '47165': 'Sumner',
    '47169': 'Trousdale',
    '47187': 'Williamson',
    '47189': 'Wilson'
}

# county select dropdown
county = st.sidebar.selectbox(
    label='label',
    label_visibility='collapsed',
    options=county_list.values(),
    index=2,
    key="county_dropdown"  
)

# sidebar separator
st.sidebar.markdown(
    "<p style='text-align:center;color:#000000;'>---------------</p>", 
    unsafe_allow_html=True
    )

# Update session state with selected county upon dropdown change
if 'county_dropdown' in st.session_state:  # Check if this is the first run
  st.session_state['selected_county'] = county

# set the dashboard subtitle now that the county has been selected
title_font_size = 30
title_margin_top = 25
title_margin_bottom = -50

st.markdown(
    f"""
    <div style='margin-top: {title_margin_top}px; margin-bottom: {title_margin_bottom}px;'>
        <span style='font-size: {title_font_size}px; font-weight: 700;'>{base_metro} Development Dashboard:</span>
        <span style='font-size: {title_font_size}px; font-weight: 200;'>{county} County Drilldown</span>
    </div>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def load_county_outline(selected_county):
    # Load county outlines from GeoPackage
    county_outline = gpd.read_file('Data/counties_simp.gpkg')

    # Define a function to filter by selected county (called within the cached function)
    def filter_by_county(selected_county):
        return county_outline[county_outline['county_stripped'] == selected_county]

    # Access selected county from session state (assuming a default is set elsewhere)
    selected_county = st.session_state.get('selected_county')

    # Filter county outlines based on selected_county
    county_outline = filter_by_county(selected_county).set_index('FIPS')

    return county_outline


# county select helper text
st.sidebar.markdown(
    "<p style='text-align:center;color:#000000;'>Map layer <br> (by Census tract):</p>", unsafe_allow_html=True)

# choropleth map variable select
attribute = st.sidebar.selectbox(
    label='label',
    label_visibility='collapsed',
    options=[
        'Total Population',
        'Senior Population', 
        'Population Density',
        'Population Growth Rate',
        'Median Household Income',
        'Homeownership Growth Rate'
    ]
)

# Define a dictionary to hold all relevant information for each attribute
attribute_info = {
    'Total Population': {
        'explanation': '2024 estimate',
        'file': f'Data/CSV/Color-coded maps - {current_year} Total Population.csv',
        'column_name': f'{current_year} Total Population',
        'number_format': lambda x: f"{x:,}",
        'colorbar_format': ',',
        'choro_color': 'Blues',
        'choro_legend': 'Population'
    },
    'Senior Population': {
        'explanation': '2024 population estimate age 65 and over',
        'file': f'Data/CSV/Color-coded maps - {current_year} Senior Population.csv',
        'column_name': f'{current_year} Senior Population',
        'number_format': lambda x: f"{x:,}",
        'colorbar_format': ',',
        'choro_color': 'Oranges',
        'choro_legend': 'Senior Population'
    },
    'Population Density': {
        'explanation': '2024 population per square mile',
        'file': f'Data/CSV/Color-coded maps - {current_year} Population Density.csv',
        'column_name': f'{current_year} Population Density',
        'number_format': lambda x: f"{x:,.0f}",
        'colorbar_format': ',',
        'choro_color': 'BuPu',
        'choro_legend': 'Population Density'
    },
    'Population Growth Rate': {
        'explanation': f'compound annual growth rate measuring the direction (either positive or negative) and magnitude of change in total population between the years {current_year} and {projected_year}',
        'file': f'Data/CSV/Color-coded maps - {current_year}-{projected_year} Growth Rate Population.csv',
        'column_name': f'{current_year}-{projected_year} Growth Rate: Population',
        'number_format': lambda x: f"{x * 100:.2f}%",
        'colorbar_format': '.2%',
        'choro_color': 'Reds',
        'choro_legend': 'Population Growth Rate'
    },
    'Median Household Income': {
        'explanation': '2024 estimate',
        'file': f'Data/CSV/Color-coded maps - {current_year} Median Household Income.csv',
        'column_name': f'{current_year} Median Household Income',
        'number_format': lambda x: f"${x:,.0f}",
        'colorbar_format': '$,',
        'choro_color': 'Greens',
        'choro_legend': 'Median Income'
    },
    'Homeownership Growth Rate': {
        'explanation': f'compound annual growth rate measuring the direction (either positive or negative) and magnitude of change in total owner-occupied housing units between the years {current_year} and {projected_year}',
        'file': f'Data/CSV/Color-coded maps - {current_year}-{projected_year} Growth Rate Owner Occ HUs.csv',
        'column_name': f'{current_year}-{projected_year} Growth Rate: Owner Occ HUs',
        'number_format': lambda x: f"{x * 100:.2f}%",
        'colorbar_format': '.1%',
        'choro_color': 'Purples',
        'choro_legend': 'Homeownership Growth Rate'
    }
}

st.sidebar.markdown(
    f"<p style='text-align:center;color:#000000;font-size: 13px;'>*{attribute_info[attribute]['explanation']}</p>", unsafe_allow_html=True
)

# sidebar separator
st.sidebar.markdown(
    "<p style='text-align:center;color:#000000;'>---------------</p>", 
    unsafe_allow_html=True
    )

# Migration variable helper text
st.sidebar.markdown(
    "<p style='text-align:center;color:#000000;'>View migration data by:</p>", unsafe_allow_html=True)

# migration chart selector
migration_variable = st.sidebar.selectbox(
   label='label',
   label_visibility='collapsed',
   options=[
        'Flow of persons',
        'Flow of dollars', 
    ],
    index=0,
)

# migration switcher
migration_switch = {
   'Flow of persons': [
       'people_net', # 0
       'People', # 1
       '~s', # 2
       '', # 3
       'Inflow - People', # 4
       'Outflow - People', # 5
       ],
    'Flow of dollars': [
        'agi_net', # 0
        'Adjusted Gross Income', # 1
        '$~s', # 2
        '$', # 3
        'Inflow - AGI', # 4
        'Outflow - AGI'# 5
        ]
}

# @st.cache_data
def load_geometry():
    # Load the geometry data
    return gpd.read_file('Data/tracts_simp.gpkg')

# @st.cache_data
def load_attribute(attribute_file):
    # Load an attribute data
    return pd.read_csv(attribute_file, dtype={'GEOID': 'str'})

# CHOROPLETH MAP ---------------------------------------------------------------------
# Load the geometry data once
geometry_gdf = load_geometry()

# Map dropdown to choropleth legend title
attribute_choroLegend = {
    'Total Population': 'Population',
    'Senior Population': 'Senior Population',
    'Population Density': 'Population Density',
    'Population Growth Rate': 'Population Growth Rate',
    'Median Household Income': 'Median Income',
    'Homeownership Growth Rate': 'Homeownership Growth Rate'
}

# Load the selected attribute data
attribute_df = load_attribute(attribute_info[attribute]['file'])
attribute_df['tooltip'] = attribute_df[attribute_info[attribute]['column_name']].apply(attribute_info[attribute]['number_format'])

# Before merging, have to format the GEOID column
def split_and_format(value):
    # Split the value on the period
    parts = value.split('.')
    # Take the first part and concatenate it with the zero-filled second part
    formatted_value = parts[0] + parts[1].zfill(2)
    return formatted_value


# Apply the function to the GEOID column
attribute_df['GEOID'] = attribute_df['GEOID'].apply(split_and_format)

# Merge geometry with attribute data
merged_gdf = geometry_gdf.merge(attribute_df, on='GEOID').set_index('GEOID')
merged_gdf['county_name'] = merged_gdf['FIPS'].map(county_list)

# get the screen height to set the heights of the map and line charts
screen_height = streamlit_js_eval(js_expressions='screen.height', key = 'SCR')

# Set default heights in case screen_height is None
default_map_height = 630
default_line_height = 220

# Calculate heights if screen_height is not None
if screen_height is not None:
    map_height = float(screen_height * 0.68)
    line_height = float(screen_height * 0.20)
else:
    map_height = default_map_height
    line_height = default_line_height

# define the main mapping figure
fig = px.choropleth_mapbox(
    merged_gdf,
    geojson=merged_gdf.geometry,
    locations=merged_gdf.index,
    color=attribute_info[attribute]['column_name'],
    color_continuous_scale=attribute_info[attribute]['choro_color'],
    custom_data=['tooltip', 'county_name'],
    labels={
        'tooltip': attribute_info[attribute]['column_name']
        },
    center={"lat": 36.00734326974716, "lon": -86.75460358901837},
    zoom=7.5,
    opacity=0.7,
    height=map_height
    )

# customize the tooltip for the choropleth map
fig.update_traces(
    hovertemplate = "<b>%{customdata[1]} County: </b>%{customdata[0]}",
    marker_line_width=0.2,
    hoverlabel=dict(font=dict(color='#000000'))  
)
# set map margin
fig.update_layout(
    margin=dict(l=10, r=10, t=20, b=1),
    mapbox_style="streets", 
    mapbox_accesstoken='pk.eyJ1Ijoid3dyaWdodDIxIiwiYSI6ImNsNW1qeDRpMDBjMHozY2tjdmdlb2RxcngifQ.od9AXX3w_r6td8tM96W_gA'
)

# style and customize the map
fig.update_coloraxes(
    colorbar_x=0.5,
    colorbar_y=0,
    colorbar_thickness=20,
    colorbar_tickformat = attribute_info[attribute]['colorbar_format'],
    colorbar_tickfont_size=12,
    colorbar_tickfont_color="rgba(0,0,0,1)",
    colorbar_title_font_size=13,
    colorbar_title_font_color="rgba(0,0,0,1)",
    colorbar_orientation='h',
    colorbar_title_text=attribute_info[attribute]['choro_legend'],
    colorbar_tickangle=60
    )

# Load the county outline
selected_county = st.session_state.get('selected_county')
county_outline = load_county_outline(selected_county)

# extract coordinates
coord_df = county_outline['geometry'].get_coordinates()

# specifically extract x (longitude) and y (latitude) values
lon = coord_df['x'].values
lat = coord_df['y'].values

# create the county outline
scatter_trace = go.Scattermapbox(
    mode='lines',
    lon=lon,
    lat=lat,
    line=dict(
        width=4, 
        color='black'
        ),
    hoverinfo='none'  
)

# add the county outline to choropleth
fig.add_trace(scatter_trace)

# hide modebar
config = {'displayModeBar': False}

# define columns
col1, col2 = st.columns([0.8,1])


# draw map
col1.write(" ")
col1.write(" ")
col1.plotly_chart(
    fig, 
    config=config,
    theme='streamlit',
    use_container_width=True
    )

# BUILDING PERMITS SECTION ---------------------------------------------------------
building_permits = pd.read_csv(
    'Data/building_permits.csv',
    dtype={
        'FIPS':'str'
    })

# filter permit data by county that is selected; keep the metro series for comparison
county_fips = str(county_outline.index[0])
building_permits = building_permits[(building_permits['FIPS'] == county_fips) | (building_permits['county_name']=='Metro')]

# vertical spacer - bumps the chart down justa hair
col2.write(" ")

# set building permit line chart colors
county_lineColor = '#000000'
metro_lineColor = '#4292c6'
tooltip_color = '#FFFFFF'

# create line chart object
fig_permits = px.line(
    building_permits,
    x='date',
    y='permit_ratio',
    color='county_name',
    labels={
       'Permits': 'Total SF Permits', 
       'permit_ratio': 'Permits per 10,000 persons',
       'county_name': 'County'
       },
    custom_data=['month_year', 'permit_ratio', 'Permits', 'county_name'],
    title='Single-Family Permits per 10,000 persons',
    height=line_height,
    color_discrete_map={
       county: county_lineColor,
       'Metro': metro_lineColor
    }
)

# configure the tooltip
fig_permits.update_traces(
    mode="markers+lines", 
    hovertemplate=
        "<b>%{customdata[0]} - %{customdata[3]}</b><br>"+
        "Per 10,000: %{customdata[1]:.2f}<br>"+
        "Total / Raw: %{customdata[2]:,}<br>"+
        "<extra></extra>",
    line=dict(width=2.5)
)

# axis tuning
fig_permits.update_xaxes(
   title=None,
   tickmode="linear", 
   dtick="M3"
   )
fig_permits.update_yaxes(title=None)
fig_permits.update_layout(
    margin=dict(l=10, r=10, t=50, b=1),
    title=dict(font=dict(size=18)),
    legend_title_text=''
)

# Loop through each trace and set hoverlabel colors
for trace in fig_permits.data:
    if trace.name == county:
        trace.hoverlabel.bgcolor = county_lineColor
        trace.hoverlabel.font.color = tooltip_color 
    elif trace.name == 'Metro':
        trace.hoverlabel.bgcolor = metro_lineColor
        trace.hoverlabel.font.color = tooltip_color

# draw building permit line chart
col2.write(" ")
col2.write(" ")
col2.plotly_chart(
    fig_permits, 
    config=config,
    theme='streamlit',
    use_container_width=True
    )

# create KPI variables
kpi_df = pd.read_csv('Data/building_permits_KPI.csv')
metro_12mo_total = kpi_df['total_permits'].sum()
county_12mo_total = kpi_df[kpi_df['county_name']==county]['total_permits'].sum()

KPI_margin_top = 2
KPI_margin_bottom = -30
KPI_label_font_size = 13
KPI_value_font_size = 16

with col2:
   subcol1, subcol2, subcol3 = st.columns(3)

# subcolumn with the county total
subcol1.markdown(
   f"""
    <div style='margin-top: {KPI_margin_top}px; margin-bottom: {KPI_margin_bottom}px;'>
        <span style='font-size: {KPI_label_font_size}px; font-weight: 200;'>12-Month <b>County</b> S.F. Total:</span><br>
        <span style='font-size: {KPI_value_font_size}px; font-weight: 800;'>{county_12mo_total:,.0f}</span>
    </div>
    """,
    unsafe_allow_html=True
)

# subcolumn with the Metro total
subcol2.markdown(
    f"""
    <div style='margin-top: {KPI_margin_top}px; margin-bottom: {KPI_margin_bottom}px;'>
        <span style='font-size: {KPI_label_font_size}px; font-weight: 200;'>12-Month <b>Metro</b> S.F. Total:</span><br>
        <span style='font-size: {KPI_value_font_size}px; font-weight: 800;'>{metro_12mo_total:,.0f}</span>
    </div>
    """,
    unsafe_allow_html=True
)

# subcolumn with the ratio of county total to metro total
subcol3.markdown(
   f"""
    <div style='margin-top: {KPI_margin_top}px; margin-bottom: {KPI_margin_bottom}px;'>
        <span style='font-size: {KPI_label_font_size}px; font-weight: 200;'>{county} County Metro Contribution:</span><br>
        <span style='font-size: {KPI_value_font_size}px; font-weight: 800;'>{county_12mo_total/metro_12mo_total*100:.1f}%</span>
    </div>
    """,
    unsafe_allow_html=True
)

col2.divider()

# IRS Migration section -------------------------------------------------------
df_irs = pd.read_csv('Data/netflow_MetroTotal.csv', dtype={
   'year': 'str',
    'FIPS': 'str'
})

df_county = df_irs[df_irs['FIPS']==county_fips]

# Create the line chart
fig_migration = px.line(
    df_county,
    x='year',
    y=migration_switch[migration_variable][0],
    color='county_name',
    custom_data=['year', 'county_name', migration_switch[migration_variable][0]],
    title=f'Net Migration Trends: {migration_switch[migration_variable][1]}',
    height=line_height,
    color_discrete_map={
       county: '#000000'
       }
    )

# hovertemplate_persons =  "<b>%{customdata[0]} - %{customdata[1]} County</b><br>"+"Net migration: %{customdata[2]:,}"+"<extra></extra>"

# hovertemplate_AGI =  "<b>%{customdata[0]} - %{customdata[1]} County</b><br>"+"Net migration: $%{customdata[2]:,}"+"<extra></extra>"


# configure the tooltip
if migration_variable == 'Flow of persons':
    fig_migration.update_traces(
        mode="markers+lines", 
        hovertemplate=None,
        hoverlabel=dict(
            bgcolor='#000000',
            font=dict(
                color='#FFFFFF'
            )),
        line=dict(width=2.5)
    )
else:
    fig_migration.update_traces(
        mode="markers+lines", 
        hovertemplate=None,
        hoverlabel=dict(
            bgcolor='#000000',
            font=dict(
                color='#FFFFFF'
            )),
        line=dict(width=2.5)
    )

# axis tuning
fig_migration.update_xaxes(
   title=None,
   tickmode="linear", 
   dtick="M3"
   )
fig_migration.update_yaxes(
    title=None,
    tickformat=migration_switch[migration_variable][2]  
    )
fig_migration.update_layout(
    margin=dict(l=10, r=10, t=50, b=1),
    title=dict(font=dict(size=18)),
    showlegend=False,
    hovermode="x unified"
)

# draw building permit line chart
col2.plotly_chart(
    fig_migration, 
    config=config,
    theme='streamlit',
    use_container_width=True
    )

# Migration KPIs
with col2:
   subcol1, subcol2 = st.columns(2)

county_netFlow = df_irs[df_irs['FIPS']==county_fips][migration_switch[migration_variable][0]].sum()
metro_netFlow = df_irs[df_irs['county_name']=='Metro'][migration_switch[migration_variable][0]].sum()

# subcolumn with the county total net migration
subcol1.markdown(
   f"""
    <div style='margin-top: {KPI_margin_top}px; margin-bottom: {KPI_margin_bottom}px;'>
        <span style='font-size: {KPI_label_font_size}px; font-weight: 200;'>5-Year <b>County</b> Net Total:</span><br>
        <span style='font-size: {KPI_value_font_size}px; font-weight: 800;'>{migration_switch[migration_variable][3]}{county_netFlow:,.0f}</span>
    </div>
    """,
    unsafe_allow_html=True
)
subcol1.write(" ")

# subcolumn with the Metro total net migration
subcol2.markdown(
    f"""
    <div style='margin-top: {KPI_margin_top}px; margin-bottom: {KPI_margin_bottom}px;'>
        <span style='font-size: {KPI_label_font_size}px; font-weight: 200;'>5-Year <b>Metro</b> Net Total:</span><br>
        <span style='font-size: {KPI_value_font_size}px; font-weight: 800;'>{migration_switch[migration_variable][3]}{metro_netFlow:,.0f}</span>
    </div>
    """,
    unsafe_allow_html=True
)
subcol2.write(" ")


countyInflow_perCapita = df_irs[df_irs['FIPS']==county_fips]['agi_inflow'].sum() / df_irs[df_irs['FIPS']==county_fips]['people_inflow'].sum()
countyOutflow_perCapita = df_irs[df_irs['FIPS']==county_fips]['agi_outflow'].sum() / df_irs[df_irs['FIPS']==county_fips]['people_outflow'].sum()

# subcolumn with the county AGI / capita inflow
subcol1.markdown(
   f"""
    <div style='margin-top: {KPI_margin_top}px; margin-bottom: {KPI_margin_bottom}px;'>
        <span style='font-size: {KPI_label_font_size}px; font-weight: 200;'>5-Year County AGI/Capita <b>Inflow</b>:</span><br>
        <span style='font-size: {KPI_value_font_size}px; font-weight: 800;'>${countyInflow_perCapita:,.0f}</span>
    </div>
    """,
    unsafe_allow_html=True
)

# subcolumn with the county AGI / capital outflow
subcol2.markdown(
    f"""
    <div style='margin-top: {KPI_margin_top}px; margin-bottom: {KPI_margin_bottom}px;'>
        <span style='font-size: {KPI_label_font_size}px; font-weight: 200;'>5-Year County AGI/Capita <b>Outflow</b>:</span><br>
        <span style='font-size: {KPI_value_font_size}px; font-weight: 800;'>${countyOutflow_perCapita:,.0f}</span>
    </div>
    """,
    unsafe_allow_html=True
)

# Migration groupby summary tables ------------------------------------------------
st.write(" ")
# st.write(" ")

# first, define a metro designation dictionary (alphabetized by metro area, not county name)
metro_clarification = {
    'Bernalillo County, NM': 'Bernalillo County, NM (Albuquerque metro)',
    'Sandoval County, NM': 'Sandoval County, NM (Albuquerque metro)',
    'Torrance County, NM': 'Torrance County, NM (Albuquerque metro)',
    'Valencia County, NM': 'Valencia County, NM (Albuquerque metro)',
    # ----
    'Buncombe County, NC': 'Buncombe County, NC (Asheville metro)',
    'Haywood County, NC': 'Haywood County, NC (Asheville metro)',
    'Henderson County, NC': 'Henderson County, NC (Asheville metro)',
    'Madison County, NC': 'Madison County, NC (Asheville metro)',
    'Transylvania County, NC': 'Transylvania County, NC (Asheville metro)',
    # ----
    'Clarke County, GA': 'Clarke County, GA (Athens metro)',
    'Madison County, GA': 'Madison County, GA (Athens metro)',
    'Oconee County, GA': 'Oconee County, GA (Athens metro)',
    'Oglethorpe County, GA': 'Oglethorpe County, GA (Athens metro)',
    # ----
    'Fulton County, GA': 'Fulton County, GA (Atlanta metro)',
    'DeKalb County, GA': 'DeKalb County, GA (Atlanta metro)',
    'Cobb County, GA': 'Cobb County, GA (Atlanta metro)',
    'Gwinnett County, GA': 'Gwinnett County, GA (Atlanta metro)',
    'Forsyth County, GA': 'Forsyth County, GA (Atlanta metro)',
    'Clayton County, GA': 'Clayton County, GA (Atlanta metro)',
    'Douglas County, GA': 'Douglas County, GA (Atlanta metro)',
    'Henry County, GA': 'Henry County, GA (Atlanta metro)',
    'Rockdale County, GA': 'Rockdale County, GA (Atlanta metro)',
    'Cherokee County, GA': 'Cherokee County, GA (Atlanta metro)',
    'Fayette County, GA': 'Fayette County, GA (Atlanta metro)',
    'Barrow County, GA': 'Barrow County, GA (Atlanta metro)',
    'Butts County, GA': 'Butts County, GA (Atlanta metro)',
    'Carroll County, GA': 'Carroll County, GA (Atlanta metro)',
    'Coweta County, GA': 'Coweta County, GA (Atlanta metro)',
    'Dawson County, GA': 'Dawson County, GA (Atlanta metro)',
    'Heard County, GA': 'Heard County, GA (Atlanta metro)',
    'Jasper County, GA': 'Jasper County, GA (Atlanta metro)',
    'Lumpkin County, GA': 'Lumpkin County, GA (Atlanta metro)',
    'Meriwether County, GA': 'Meriwether County, GA (Atlanta metro)',
    'Morgan County, GA': 'Morgan County, GA (Atlanta metro)',
    'Newton County, GA': 'Newton County, GA (Atlanta metro)',
    'Pickens County, GA': 'Pickens County, GA (Atlanta metro)',
    'Pike County, GA': 'Pike County, GA (Atlanta metro)',
    'Spalding County, GA': 'Spalding County, GA (Atlanta metro)',
    'Walton County, GA': 'Walton County, GA (Atlanta metro)',
    'Bartow County, GA': 'Bartow County, GA (Atlanta metro)',
    'Haralson County, GA': 'Haralson County, GA (Atlanta metro)',
    'Paulding County, GA': 'Paulding County, GA (Atlanta metro)',
    # ----
    'Brevard County, FL': 'Brevard County, FL (Atlantic Coast)',
    'Volusia County, FL': 'Volusia County, FL (Atlantic Coast)',
    'Flagler County, FL': 'Flagler County, FL (Atlantic Coast)',
    'Indian River County, FL': 'Indian River County, FL (Atlantic Coast)',
    'St. Lucie County, FL': 'St. Lucie County, FL (Atlantic Coast)',
    'Martin County, FL': 'Martin County, FL (Atlantic Coast)',
    # ----
    'Travis County, TX': 'Travis County, TX (Austin metro)',
    'Bastrop County, TX': 'Bastrop County, TX (Austin metro)',
    'Hays County, TX': 'Hays County, TX (Austin metro)',
    'Travis County, TX': 'Travis County, TX (Austin metro)',
    'Williamson County, TX': 'Williamson County, TX (Austin metro)',
    # ----
    'Augusta-Richmond County, GA': 'Augusta-Richmond County, GA (Augusta metro)',
    'Columbia County, GA': 'Columbia County, GA (Augusta metro)',
    'Aiken County, SC': 'Aiken County, SC (Augusta metro)',
    # ----
    'Baltimore city, MD': 'Baltimore city, MD (Baltimore metro)',
    'Baltimore County, MD': 'Baltimore County, MD (Baltimore metro)',
    'Anne Arundel County, MD': 'Anne Arundel County, MD (Baltimore metro)',
    'Carroll County, MD': 'Carroll County, MD (Baltimore metro)',
    'Harford County, MD': 'Harford County, MD (Baltimore metro)',
    'Howard County, MD': 'Howard County, MD (Baltimore metro)',
    'Queen Anne\'s County, MD': 'Queen Anne\'s County, MD (Baltimore metro)',
    # ----
    'Alameda County, CA': 'Alameda County, CA (Bay Area)',
    'San Mateo County, CA': 'San Mateo County, CA (Bay Area)',
    'San Francisco County, CA': 'San Francisco County, CA (Bay Area)',
    'Santa Clara County, CA': 'Santa Clara County, CA (Bay Area)',
    'Contra Costa County, CA': 'Contra Costa County, CA (Bay Area)',
    'Marin County, CA': 'Marin County, CA (Bay Area)',
    'Napa County, CA': 'Napa County, CA (Bay Area)',
    'Solano County, CA': 'Solano County, CA (Bay Area)',
    'Sonoma County, CA': 'Sonoma County, CA (Bay Area)',
    'San Benito County, CA': 'San Benito County, CA (Bay Area)',
    'Merced County, CA': 'Merced County, CA (Bay Area)',
    'Santa Cruz County, CA': 'Santa Cruz County, CA (Bay Area)',
    'San Joaquin County, CA': 'San Joaquin County, CA (Bay Area)',
    'Stanislaus County, CA': 'Stanislaus County, CA (Bay Area)',
    # ----
    'Jefferson County, AL': 'Jefferson County, AL (Birmingham metro)',
    'Bibb County, AL': 'Bibb County, AL (Birmingham metro)',
    'Blount County, AL': 'Blount County, AL (Birmingham metro)',
    'Chilton County, AL': 'Chilton County, AL (Birmingham metro)',
    'St. Clair County, AL': 'St. Clair County, AL (Birmingham metro)',
    'Shelby County, AL': 'Shelby County, AL (Birmingham metro)',
    'Walker County, AL': 'Walker County, AL (Birmingham metro)',
    'Coosa County, AL': 'Coosa County, AL (Birmingham metro)',
    'Talladega County, AL': 'Talladega County, AL (Birmingham metro)',
    'Cullman County, AL': 'Cullman County, AL (Birmingham metro)',
    # ----
    'Essex County, MA': 'Essex County, MA (Boston metro)',
    'Middlesex County, MA': 'Middlesex County, MA (Boston metro)',
    'Suffolk County, MA': 'Suffolk County, MA (Boston metro)',
    'Norfolk County, MA': 'Norfolk County, MA (Boston metro)',
    'Plymouth County, MA': 'Plymouth County, MA (Boston metro)',
    'Rockingham County, MA': 'Rockingham County, MA (Boston metro)',
    'Strafford County, MA': 'Strafford County, MA (Boston metro)',
    # ----
    'Erie County, NY': 'Erie County, NY (Buffalo metro)',
    'Niagara County, NY': 'Niagara County, NY (Buffalo metro)',
    'Cattaraugus County, NY': 'Cattaraugus County, NY (Buffalo metro)',
    # ----
    'Charleston County, SC': 'Charleston County, SC (Charleston metro)',
    'Berkeley County, SC': 'Berkeley County, SC (Charleston metro)',
    'Dorchester County, SC': 'Dorchester County, SC (Charleston metro)',
    # ----
    'Mecklenburg County, NC': 'Mecklenburg County, NC (Charlotte metro)',
    'York County, SC': 'York County, SC (Charlotte metro)',
    'Union County, NC': 'Union County, NC (Charlotte metro)',
    'Cabarrus County, NC': 'Cabarrus County, NC (Charlotte metro)',
    'Gaston County, NC': 'Gaston County, NC (Charlotte metro)',
    'Iredell County, NC': 'Iredell County, NC (Charlotte metro)',
    'Rowan County, NC': 'Rowan County, NC (Charlotte metro)',
    'Lancaster County, NC': 'Lancaster County, NC (Charlotte metro)',
    'Lincoln County, NC': 'Lincoln County, NC (Charlotte metro)',
    # ----
    'Hamilton County, TN': 'Hamilton County, TN (Chattanooga metro)',
    'Bradley County, TN': 'Bradley County, TN (Chattanooga metro)',
    'Catoosa County, GA': 'Catoosa County, GA (Chattanooga metro)',
    'Dade County, GA': 'Dade County, GA (Chattanooga metro)',
    'Marion County, TN': 'Marion County, TN (Chattanooga metro)',
    'Sequatchie County, TN': 'Sequatchie County, TN (Chattanooga metro)',
    'Walker County, GA': 'Walker County, GA (Chattanooga metro)',
    # ----
    'Cook County, IL': 'Cook County, IL (Chicago metro)',
    'Lake County, IL': 'Lake County, IL (Chicago metro)',
    'DuPage County, IL': 'DuPage County, IL (Chicago metro)',
    'Will County, IL': 'Will County, IL (Chicago metro)',
    'Kane County, IL': 'Kane County, IL (Chicago metro)',
    'Kendall County, IL': 'Kendall County, IL (Chicago metro)',
    'McHenry County, IL': 'McHenry County, IL (Chicago metro)',
    # ----
    'Hamilton County, OH': 'Hamilton County, OH (Cincinnati metro)',
    'Campbell County, KY': 'Campbell County, KY (Cincinnati metro)',
    'Kenton County, KY': 'Kenton County, KY (Cincinnati metro)',
    'Boone County, KY': 'Boone County, KY (Cincinnati metro)',
    'Butler County, OH': 'Butler County, OH (Cincinnati metro)',
    # ----
    'Cuyahoga County, OH': 'Cuyahoga County, OH (Cleveland metro)',
    'Lorain County, OH': 'Lorain County, OH (Cleveland metro)',
    'Lake County, OH': 'Lake County, OH (Cleveland metro)',
    'Medina County, OH': 'Medina County, OH (Cleveland metro)',
    'Ashtabula County, OH': 'Ashtabula County, OH (Cleveland metro)',
    'Geauga County, OH': 'Geauga County, OH (Cleveland metro)',
    # ----
    'El Paso County, CO': 'El Paso County, CO (Colorado Springs metro)',
    'Teller County, CO': 'Teller County, CO (Colorado Springs metro)',
    # ----
    'Calhoun County, SC': 'Calhoun County, SC (Columbia metro)',
    'Fairfield County, SC': 'Fairfield County, SC (Columbia metro)',
    'Kershaw County, SC': 'Kershaw County, SC (Columbia metro)',
    'Lexington County, SC': 'Lexington County, SC (Columbia metro)',
    'Richland County, SC': 'Richland County, SC (Columbia metro)',
    'Saluda County, SC': 'Saluda County, SC (Columbia metro)',
    # ----
    'Boone County, MO': 'Boone County, MO (Columbia metro)',
    # ----
    'Franklin County, OH': 'Franklin County, OH (Columbus metro)',
    'Delaware County, OH': 'Delaware County, OH (Columbus metro)',
    # ----
    'Arlington County, VA': 'Arlington County, VA (D.C. metro)',
    'Alexandria city, VA': 'Alexandria city, VA (D.C. metro)',
    'District of Columbia, DC': 'District of Columbia, DC (D.C. metro)',
    'Fairfax County, VA': 'Fairfax County, VA (D.C. metro)',
    'Montgomery County, MD': 'Montgomery County, MD (D.C. metro)',
    # ----
    'Dallas County, TX': 'Dallas County, TX (Dallas-Fort Worth metro)',
    'Denton County, TX': 'Denton County, TX (Dallas-Fort Worth metro)',
    'Tarrant County, TX': 'Tarrant County, TX (Dallas-Fort Worth metro)',
    'Collin County, TX': 'Collin County, TX (Dallas-Fort Worth metro)',
    'Ellis County, TX': 'Ellis County, TX (Dallas-Fort Worth metro)',
    'Hunt County, TX': 'Hunt County, TX (Dallas-Fort Worth metro)',
    'Kaufman County, TX': 'Kaufman County, TX (Dallas-Fort Worth metro)',
    'Rockwall County, TX': 'Rockwall County, TX (Dallas-Fort Worth metro)',
    'Johnson County, TX': 'Johnson County, TX (Dallas-Fort Worth metro)',
    'Parker County, TX': 'Parker County, TX (Dallas-Fort Worth metro)',
    'Wise County, TX': 'Wise County, TX (Dallas-Fort Worth metro)',
    # ----
    'Denver County, CO': 'Denver County, CO (Denver metro)',
    'Arapahoe County, CO': 'Arapahoe County, CO (Denver metro)',
    'Jefferson County, CO': 'Jefferson County, CO (Denver metro)',
    'Adams County, CO': 'Adams County, CO (Denver metro)',
    'Douglas County, CO': 'Douglas County, CO (Denver metro)',
    'Boulder County, CO': 'Boulder County, CO (Denver metro)',
    # ----
    'Oakland County, MI': 'Oakland County, MI (Detroit metro)',
    'Wayne County, MI': 'Wayne County, MI (Detroit metro)',
    # ----
     'El Paso County, TX': 'El Paso County, TX (El Paso metro)',
     'Hudspeth County, TX': 'Hudspeth County, TX (El Paso metro)',
    # ----
    'Guilford County, NC': 'Guilford County, NC (Greensboro metro)',
    'Forsyth County, NC': 'Forsyth County, NC (Greensboro metro)',
    'Alamance County, NC': 'Alamance County, NC (Greensboro metro)',
    'Davidson County, NC': 'Davidson County, NC (Greensboro metro)',
    'Randolph County, NC': 'Randolph County, NC (Greensboro metro)',
    'Rockingham County, NC': 'Rockingham County, NC (Greensboro metro)',
    'Surry County, NC': 'Surry County, NC (Greensboro metro)',
    'Stokes County, NC': 'Stokes County, NC (Greensboro metro)',
    'Davie County, NC': 'Davie County, NC (Greensboro metro)',
    'Yadkin County, NC': 'Yadkin County, NC (Greensboro metro)',
    # ----
    'Greenville County, SC': 'Greenville County, SC (Greenville metro)',
    'Spartanburg County, SC': 'Spartanburg County, SC (Greenville metro)',
    'Anderson County, SC': 'Anderson County, SC (Greenville metro)',
    'Pickens County, SC': 'Pickens County, SC (Greenville metro)',
    'Oconee County, SC': 'Oconee County, SC (Greenville metro)',
    # ----
    'Harris County, TX': 'Harris County, TX (Houston metro)',
    'Austin County, TX': 'Austin County, TX (Houston metro)',
    'Brazoria County, TX': 'Brazoria County, TX (Houston metro)',
    'Chambers County, TX': 'Chambers County, TX (Houston metro)',
    'Fort Bend County, TX': 'Fort Bend County, TX (Houston metro)',
    'Galveston County, TX': 'Galveston County, TX (Houston metro)',
    'Liberty County, TX': 'Liberty County, TX (Houston metro)',
    'Montgomery County, TX': 'Montgomery County, TX (Houston metro)',
    'Waller County, TX': 'Waller County, TX (Houston metro)',
    # ----
    'Madison County, AL': 'Madison County, AL (Huntsville metro)',
    'Limestone County, AL': 'Limestone County, AL (Huntsville metro)',
    # ----
    'Marion County, IN': 'Marion County, IN (Indianapolis metro)',
    'Hamilton County, IN': 'Hamilton County, IN (Indianapolis metro)',
    'Hendricks County, IN': 'Hendricks County, IN (Indianapolis metro)',
    'Johnson County, IN': 'Johnson County, IN (Indianapolis metro)',
    'Madison County, IN': 'Madison County, IN (Indianapolis metro)',
    # ----
    'Copiah County, MS': 'Copiah County, MS (Jackson metro)',
    'Hinds County, MS': 'Hinds County, MS (Jackson metro)',
    'Holmes County, MS': 'Holmes County, MS (Jackson metro)',
    'Madison County, MS': 'Madison County, MS (Jackson metro)',
    'Rankin County, MS': 'Rankin County, MS (Jackson metro)',
    'Simpson County, MS': 'Simpson County, MS (Jackson metro)',
    'Yazoo County, MS': 'Yazoo County, MS (Jackson metro)',
    # ----
    'Duval County, FL': 'Duval County, FL (Jacksonville metro)',
    'St. Johns County, FL': 'St. Johns County, FL (Jacksonville metro)',
    'Clay County, FL': 'Clay County, FL (Jacksonville metro)',
    'Nassau County, FL': 'Nassau County, FL (Jacksonville metro)',
    'Baker County, FL': 'Baker County, FL (Jacksonville metro)',
    # ----
    'Knox County, TN': 'Knox County, TN (Knoxville metro)',
    'Loudon County, TN': 'Loudon County, TN (Knoxville metro)',
    # ----
    'Clark County, NV': 'Clark County, NV (Las Vegas metro)',
    # ----
    'Fayette County, KY': 'Fayette County, KY (Lexington metro)',
    # ----
    'Pulaski County, AR': 'Pulaski County, AR (Little Rock metro)',
    'Faulkner County, AR': 'Faulkner County, AR (Little Rock metro)',
    'Grant County, AR': 'Grant County, AR (Little Rock metro)',
    'Lonoke County, AR': 'Lonoke County, AR (Little Rock metro)',
    'Perry County, AR': 'Perry County, AR (Little Rock metro)',
    'Saline County, AR': 'Saline County, AR (Little Rock metro)',
    # ----
    'Orange County, CA': 'Orange County, CA (Los Angeles metro)',
    'Los Angeles County, CA': 'Los Angeles County, CA (Los Angeles metro)',
    'Riverside County, CA': 'Riverside County, CA (Los Angeles metro)',
    'San Bernardino County, CA': 'San Bernardino County, CA (Los Angeles metro)',
    'Ventura County, CA': 'Ventura County, CA (Los Angeles metro)',
    # ----
    'Jefferson County, KY': 'Jefferson County, KY (Louisville metro)',
    'Clark County, IN': 'Clark County, IN (Louisville metro)',
    # ----
    'Dane County, WI': 'Dane County, WI (Madison metro)',
    # ----
    'Shelby County, TN': 'Shelby County, TN (Memphis metro)',
    'Fayette County, TN': 'Fayette County, TN (Memphis metro)',
    'Tipton County, TN': 'Tipton County, TN (Memphis metro)',
    'DeSoto County, MS': 'DeSoto County, MS (Memphis metro)',
    'Crittenden County, AR': 'Crittenden County, AR (Memphis metro)',
    'Marshall County, MS': 'Marshall County, MS (Memphis metro)',
    'Tate County, MS': 'Tate County, MS (Memphis metro)',
    # ----
    'Miami-Dade County, FL': 'Miami-Dade County, FL (Miami metro)',
    'Palm Beach County, FL': 'Palm Beach County, FL (Miami metro)',
    'Broward County, FL': 'Broward County, FL (Miami metro)',
    # ----
    'Milwaukee County, WI': 'Milwaukee County, WI (Milwaukee metro)',
    'Waukesha County, WI': 'Waukesha County, WI (Milwaukee metro)',
    'Dodge County, WI': 'Dodge County, WI (Milwaukee metro)',
    'Jefferson County, WI': 'Jefferson County, WI (Milwaukee metro)',
    'Ozaukee County, WI': 'Ozaukee County, WI (Milwaukee metro)',
    'Racine County, WI': 'Racine County, WI (Milwaukee metro)',
    'Walworth County, WI': 'Walworth County, WI (Milwaukee metro)',
    'Washington County, WI': 'Washington County, WI (Milwaukee metro)',
    # ----
    'Hennepin County, MN': 'Hennepin County, MN (Minneapolis metro)',
    'Ramsey County, MN': 'Ramsey County, MN (Minneapolis metro)',
    'Dakota County, MN': 'Dakota County, MN (Minneapolis metro)',
    'Anoka County, MN': 'Anoka County, MN (Minneapolis metro)',
    'Washington County, MN': 'Washington County, MN (Minneapolis metro)',
    'Scott County, MN': 'Scott County, MN (Minneapolis metro)',
    'Wright County, MN': 'Wright County, MN (Minneapolis metro)',
    'Carver County, MN': 'Carver County, MN (Minneapolis metro)',
    'Sherburne County, MN': 'Sherburne County, MN (Minneapolis metro)',
    'St. Croix County, WI': 'St. Croix County, WI (Minneapolis metro)',
    # ----
    'Mobile County, AL': 'Mobile County, AL (Mobile metro)',
    'Baldwin County, AL': 'Baldwin County, AL (Mobile metro)',
    # ----
    'Autauga County, AL': 'Autauga County, AL (Montgomery metro)',
    'Elmore County, AL': 'Elmore County, AL (Montgomery metro)',
    'Lowndes County, AL': 'Lowndes County, AL (Montgomery metro)',
    'Montgomery County, AL': 'Montgomery County, AL (Montgomery metro)',
    # ----
    'Cannon County, TN': 'Cannon County, TN (Nashville metro)',
    'Cheatham County, TN': 'Cheatham County, TN (Nashville metro)',
    'Davidson County, TN': 'Davidson County, TN (Nashville metro)',
    'Dickson County, TN': 'Dickson County, TN (Nashville metro)',
    'Hickman County, TN': 'Hickman County, TN (Nashville metro)',
    'Macon County, TN': 'Macon County, TN (Nashville metro)',
    'Maury County, TN': 'Maury County, TN (Nashville metro)',
    'Robertson County, TN': 'Robertson County, TN (Nashville metro)',
    'Rutherford County, TN': 'Rutherford County, TN (Nashville metro)',
    'Smith County, TN': 'Smith County, TN (Nashville metro)',
    'Sumner County, TN': 'Sumner County, TN (Nashville metro)',
    'Trousdale County, TN': 'Trousdale County, TN (Nashville metro)',
    'Williamson County, TN': 'Williamson County, TN (Nashville metro)',
    'Wilson County, TN': 'Wilson County, TN (Nashville metro)',
    # ----
    'Jefferson Parish, LA': 'Jefferson Parish, LA (New Orleans metro)',
    'Orleans Parish, LA': 'Orleans Parish, LA (New Orleans metro)',
    'Plaquemines Parish, LA': 'Plaquemines Parish, LA (New Orleans metro)',
    'St. Bernard Parish, LA': 'St. Bernard Parish, LA (New Orleans metro)',
    'St. Charles Parish, LA': 'St. Charles Parish, LA (New Orleans metro)',
    'St. James Parish, LA': 'St. James Parish, LA (New Orleans metro)',
    'St. John the Baptist Parish, LA': 'St. John the Baptist Parish, LA (New Orleans metro)',
    'St. Tammany Parish, LA': 'St. Tammany Parish, LA (New Orleans metro)',
    # ----
    'Kings County, NY': 'Kings County, NY (New York Metro)',
    'Queens County, NY': 'Queens County, NY (New York Metro)',
    'New York County, NY': 'New York County, NY (New York metro)',
    'Bronx County, NY': 'Bronx County, NY (New York Metro)',
    'Richmond County, NY': 'Richmond County, NY (New York Metro)',
    'Westchester County, NY': 'Westchester County, NY (New York metro)',
    'Bergen County, NJ': 'Bergen County, NJ (New York metro)',
    'Hudson County, NJ': 'Hudson County, NJ (New York metro)',
    'Passaic County, NJ': 'Passaic County, NJ (New York metro)',
    'Rockland County, NY': 'Rockland County, NY (New York Metro)',
    'Putnam County, NY': 'Putnam County, NY (New York Metro)',
    'Suffolk County, NY': 'Suffolk County, NY (New York Metro)',
    'Nassau County, NY': 'Nassau County, NY (New York Metro)',
    'Middlesex County, NJ': 'Middlesex County, NJ (New York metro)',
    'Monmouth County, NJ': 'Monmouth County, NJ (New York metro)',
    'Ocean County, NJ': 'Ocean County, NJ (New York metro)',
    'Somerset County, NJ': 'Somerset County, NJ (New York metro)',
    'Essex County, NJ': 'Essex County, NJ (New York metro)',
    'Union County, NJ': 'Union County, NJ (New York metro)',
    'Morris County, NJ': 'Morris County, NJ (New York metro)',
    'Sussex County, NJ': 'Sussex County, NJ (New York metro)',
    'Hunterdon County, NJ': 'Hunterdon County, NJ (New York Metro)',
    'Pike County, PA': 'Pike County, PA (New York Metro)',
    'Fairfield County, CT': 'Fairfield County, CT (New York metro)',
    # ----
    'Douglas County, NE': 'Douglas County, NE (Omaha metro)',
    'Sarpy County, NE': 'Sarpy County, NE (Omaha metro)',
    # ----
    'Orange County, FL': 'Orange County, FL (Orlando metro)',
    'Polk County, FL': 'Polk County, FL (Orlando metro)',
    'Seminole County, FL': 'Seminole County, FL (Orlando metro)',
    'Osceola County, FL': 'Osceola County, FL (Orlando metro)',
    'Lake County, FL': 'Lake County, FL (Orlando metro)',
    # ----
    'Walton County, FL': 'Walton County, FL (Panhandle)',
    'Bay County, FL': 'Bay County, FL (Panhandle)',
    'Escambia County, FL': 'Escambia County, FL (Panhandle)',
    'Calhoun County, FL': 'Calhoun County, FL (Panhandle)',
    'Okaloosa County, FL': 'Okaloosa County, FL (Panhandle)',
    'Gulf County, FL': 'Gulf County, FL (Panhandle)',
    'Holmes County, FL': 'Holmes County, FL (Panhandle)',
    'Jackson County, FL': 'Jackson County, FL (Panhandle)',
    'Santa Rosa County, FL': 'Santa Rosa County, FL (Panhandle)',
    'Washington County, FL': 'Washington County, FL (Panhandle)',
    # ----
    'Philadelphia County, PA': 'Philadelphia County, PA (Philadelphia metro)',
    'Montgomery County, PA': 'Montgomery County, PA (Philadelphia metro)',
    'Delaware County, PA': 'Delaware County, PA (Philadelphia metro)',
    'Chester County, PA': 'Chester County, PA (Philadelphia metro)',
    'Bucks County, PA': 'Bucks County, PA (Philadelphia metro)',
    'Burlington County, NJ': 'Burlington County, NJ (Philadelphia metro)',
    'Camden County, NJ': 'Camden County, NJ (Philadelphia metro)',
    'Gloucester County, NJ': 'Gloucester County, NJ (Philadelphia metro)',
    # ----
    'Maricopa County, AZ': 'Maricopa County, AZ (Phoenix metro)',
    'Pinal County, AZ': 'Pinal County, AZ (Phoenix metro)',
    'Gila County, AZ': 'Gila County, AZ (Phoenix metro)',
    # ----
    'Allegheny County, PA': 'Allegheny County, PA (Pittsburgh metro)',
    'Beaver County, PA': 'Beaver County, PA (Pittsburgh metro)',
    'Butler County, PA': 'Butler County, PA (Pittsburgh metro)',
    'Fayette County, PA': 'Fayette County, PA (Pittsburgh metro)',
    'Washington County, PA': 'Washington County, PA (Pittsburgh metro)',
    'Westmoreland County, PA': 'Westmoreland County, PA (Pittsburgh metro)',
    # ----
    'Multnomah County, OR': 'Multnomah County, OR (Portland metro)',
    'Washington County, OR': 'Washington County, OR (Portland metro)',
    'Clark County, WA': 'Clark County, WA (Portland metro)',
    'Clackamas County, OR': 'Clackamas County, OR (Portland metro)',
    'Yamhill County, OR': 'Yamhill County, OR (Portland metro)',
    'Columbia County, OR': 'Columbia County, OR (Portland metro)',
    'Skamania County, OR': 'Skamania County, OR (Portland metro)',
    # ----
    'Cumberland County, ME': 'Cumberland County, ME (Portland metro)',
    'Sagadahoc County, ME': 'Sagadahoc County, ME (Portland metro)',
    'York County, ME': 'York County, ME (Portland metro)',
    'Androscoggin County, ME': 'Androscoggin County, ME (Portland metro)',
    # ----
    'Wake County, NC': 'Wake County, NC (Raleigh metro)',
    'Durham County, NC': 'Durham County, NC (Raleigh metro)',
    'Chatham County, NC': 'Chatham County, NC (Raleigh metro)',
    'Orange County, NC': 'Orange County, NC (Raleigh metro)',
    'Franklin County, NC': 'Franklin County, NC (Raleigh metro)',
    'Johnston County, NC': 'Johnston County, NC (Raleigh metro)',
    'Vance County, NC': 'Vance County, NC (Raleigh metro)',
    # ----
    'Richmond city, VA': 'Richmond city, VA (Richmond metro)',
    'Petersburg city, VA': 'Petersburg city, VA (Richmond metro)',
    'Hopewell city, VA': 'Hopewell city, VA (Richmond metro)',
    'Colonial Heights city, VA': 'Colonial Heights city, VA (Richmond metro)',
    'Chesterfield County, VA': 'Chesterfield County, VA (Richmond metro)',
    'Hanover County, VA': 'Hanover County, VA (Richmond metro)',
    'Henrico County, VA': 'Henrico County, VA (Richmond metro)',
    'Goochland County, VA': 'Goochland County, VA (Richmond metro)',
    # ----
    'Monroe County, NY': 'Monroe County, NY (Rochester metro)',
    # ----
    'Sacramento County, CA': 'Sacramento County, CA (Sacramento metro)',
    'Placer County, CA': 'Placer County, CA (Sacramento metro)',
    'El Dorado County, CA': 'El Dorado County, CA (Sacramento metro)',
    'Nevada County, CA': 'Nevada County, CA (Sacramento metro)',
    'Sutter County, CA': 'Sutter County, CA (Sacramento metro)',
    'Yolo County, CA': 'Yolo County, CA (Sacramento metro)',
    'Yuba County, CA': 'Yuba County, CA (Sacramento metro)',
    # ----
    'Salt Lake County, UT': 'Salt Lake County, UT (S.L.C. metro)',
    'Tooele County, UT': 'Tooele County, UT (S.L.C. metro)',
    # ----
    'Bexar County, TX': 'Bexar County, TX (San Antonio metro)',
    'Comal County, TX': 'Comal County, TX (San Antonio metro)',
    'Guadalupe County, TX': 'Guadalupe County, TX (San Antonio metro)',
    # ----
    'San Diego County, CA': 'San Diego County, CA (San Diego metro)',
    # ----
    'Chatham County, GA': 'Chatham County, GA (Savannah metro)',
    'Effingham County, GA': 'Effingham County, GA (Savannah metro)',
    'Bryan County, GA': 'Bryan County, GA (Savannah metro)',
    'Beaufort County, SC': 'Beaufort County, SC (Savannah metro)',
    'Jasper County, SC': 'Jasper County, SC (Savannah metro)',
    # ----
    'King County, WA': 'King County, WA (Seattle metro)',
    'Pierce County, WA': 'Pierce County, WA (Seattle metro)',
    'Snohomish County, WA': 'Snohomish County, WA (Seattle metro)',
    # ----
    'Spokane County, WA': 'Spokane County, WA (Spokane metro)',
    'Stevens County, WA': 'Stevens County, WA (Spokane metro)',
    # ----
    'St. Louis County, MO': 'St. Louis County, MO (St. Louis metro)',
    'St. Charles County, MO': 'St. Charles County, MO (St. Louis metro)',
    'St. Louis City, MO': 'St. Louis City, MO (St. Louis metro)',
    'Madison County, IL': 'Madison County, IL (St. Louis metro)',
    'St. Clair County, IL': 'St. Clair County, IL (St. Louis metro)',
    'Jefferson County, MO': 'Jefferson County, MO (St. Louis metro)',
    'Franklin County, MO': 'Franklin County, MO (St. Louis metro)',
    # ----
    'Collier County, FL': 'Collier County, FL (S.W. Florida)',
    'Lee County, FL': 'Lee County, FL (S.W. Florida)',
    'Sarasota County, FL': 'Sarasota County, FL (S.W. Florida)',
    'Charlotte County, FL': 'Charlotte County, FL (S.W. Florida)',
    'Monroe County, FL': 'Monroe County, FL (S.W. Florida)',
    # ----
    'Hillsborough County, FL': 'Hillsborough County, FL (Tampa metro)',
    'Pinellas County, FL': 'Pinellas County, FL (Tampa metro)',
    'Pasco County, FL': 'Pasco County, FL (Tampa metro)',
    'Hernando County, FL': 'Hernando County, FL (Tampa metro)',
}

# inflow table xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# st.divider()
st.markdown(
    f"""
    <div style='margin-top: 20px; margin-bottom: 20px; text-align: center;'>
        <span style='font-size: 17px; font-weight: 700;'>
            {county} County Migration Inflow Summary Table (2018-2022):
        </span>
    </div>
    """,
    unsafe_allow_html=True
)

inflow_County2County = pd.read_csv(
    'Data/inflow_County2County.csv', 
    dtype={
        'origin_FIPS': 'str',
        'destination_FIPS': 'str'
    }
    )
inflow_County2County = inflow_County2County[inflow_County2County['destination_FIPS']==county_fips]

inflow_summary = inflow_County2County.groupby('origin_county').agg({
    'people_inflow': 'sum',
    'agi_inflow': 'sum'
}).reset_index()

inflow_summary = inflow_summary.rename(columns={
    'origin_county': 'Origin County',
    'people_inflow': 'Inflow - People',
    'agi_inflow': 'Inflow - AGI'    
})

inflow_summary['AGI / Capita'] = inflow_summary['Inflow - AGI'] / inflow_summary['Inflow - People']

# non-exhaustive mapping of metro clarification names for county names
inflow_summary['Origin County'] = inflow_summary['Origin County'].map(metro_clarification).fillna(inflow_summary['Origin County'])

# create styler
inflow_summary_formatted = inflow_summary.style.format(
    {
        "Inflow - AGI": lambda x: '${:,.0f}'.format(x),
        "Average AGI / Capita": lambda x: '${:,.2f}'.format(x)
    },
    thousands=','
)

# show interactive table
st.dataframe(
    inflow_summary_formatted, 
    use_container_width=True, 
    height=300,
    hide_index=True
    )

# get metro area as separate column
inflow_summary['Metro Area'] = inflow_summary['Origin County'].str.extract(r'\((.*?)\)', expand=False).str.replace(' metro', '', regex=False)

# Determine the number of unique metro areas, up to a maximum of 5
unique_metro_areas = inflow_summary['Metro Area'].nunique()

# group on the Metro area to get top receiving metros
top_sending = inflow_summary.groupby('Metro Area')[f'{migration_switch[migration_variable][4]}'].sum().reset_index()

# drop the base metro, since inter-metro migration will top the list every time
top_sending = top_sending[~top_sending['Metro Area'].str.contains(base_metro)]
n = min(len(top_sending), 5)

top_n = top_sending.sort_values(by=f'{migration_switch[migration_variable][4]}', ascending=False).head(n)

# Store the results in separate variables
metro_areas = top_n['Metro Area'].tolist()
inflow_variable = top_n[f'{migration_switch[migration_variable][4]}'].tolist()

# set KPI styling
margin_top = 15
margin_bottom = 10
font_size = 15

# code to dynamically show top 5, top 4, etc. metros for the given county
if n>0:

    # set the heading
    st.markdown(
        f"""
            <div style='margin-top: 20px; margin-bottom: 20px; text-align: center;'>
                <span style='font-size: 16px; font-weight: 200;'>
                    Top Sending Metros into {county} County (does not include {base_metro} metro):
                </span>
            </div>
        """,
    unsafe_allow_html=True)

    # set columns dynamically
    cols = st.columns(n)

    for i in range(n):
        cols[i].markdown(
            f"""
                <div style='margin-top: {margin_top}px; margin-bottom: {margin_bottom}px; text-align: center;'>
                    <div style='align-items: center;'><span style='font-size: 18px; font-weight: 700;'>{i+1}</span></div>
                    <span style='font-size: {font_size}px; font-weight: 200;'>
                        {metro_areas[i]}<br>{migration_switch[migration_variable][3]}{inflow_variable[i]:,}
                    </span>
                </div>
            """,
            unsafe_allow_html=True)
else:
    st.markdown(
        f"""
            <div style='margin-top: {margin_top}px; margin-bottom: {margin_bottom}px; text-align: center;'>
                <span style='font-size: 16px; font-weight: 200;'>
                    No counted migration into {county} County from outside the {base_metro} metro area (or rural areas).
                </span>
            </div>
        """,
            unsafe_allow_html=True)

st.divider()

# outflow table xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
st.markdown(
    f"""
    <div style='margin-top: 20px; margin-bottom: 20px; text-align: center;'>
        <span style='font-size: 17px; font-weight: 700;'>
            {county} County Migration Outflow Summary Table (2018-2022):
        </span>
    </div>
    """,
    unsafe_allow_html=True
)

outflow_County2County = pd.read_csv(
    'Data/outflow_County2County.csv', 
    dtype={
        'origin_FIPS': 'str',
        'destination_FIPS': 'str'
    }
    )
outflow_County2County = outflow_County2County[outflow_County2County['origin_FIPS']==county_fips]

outflow_summary = outflow_County2County.groupby('destination_county').agg({
    'people_outflow': 'sum',
    'agi_outflow': 'sum'
}).reset_index()

outflow_summary = outflow_summary.rename(columns={
    'destination_county': 'Destination County',
    'people_outflow': 'Outflow - People',
    'agi_outflow': 'Outflow - AGI'    
})

outflow_summary['AGI / Capita'] = outflow_summary['Outflow - AGI'] / outflow_summary['Outflow - People']

# non-exhaustive mapping of metro clarification names for county names
outflow_summary['Destination County'] = outflow_summary['Destination County'].map(metro_clarification).fillna(outflow_summary['Destination County'])

outflow_summary_formatted = outflow_summary.style.format(
    {
        "Outflow - AGI": lambda x: '${:,.0f}'.format(x),
        "Average AGI / Capita": lambda x: '${:,.2f}'.format(x)
    },
    thousands=','
)

# show interactive table
st.dataframe(
    outflow_summary_formatted, 
    use_container_width=True, 
    height=300,
    hide_index=True
    )

# get metro area as separate column
outflow_summary['Metro Area'] = outflow_summary['Destination County'].str.extract(r'\((.*?)\)', expand=False).str.replace(' metro', '', regex=False)

# Determine the number of unique metro areas, up to a maximum of 5
unique_metro_areas = outflow_summary['Metro Area'].nunique()

# group on the Metro area to get top receiving metros
top_receiving = outflow_summary.groupby('Metro Area')[f'{migration_switch[migration_variable][5]}'].sum().reset_index()

# drop the base metro, since inter-metro migration will top the list every time
top_receiving = top_receiving[~top_receiving['Metro Area'].str.contains(base_metro)]
n = min(len(top_receiving), 5)

top_n = top_receiving.sort_values(by=f'{migration_switch[migration_variable][5]}', ascending=False).head(n)

# Store the results in separate variables
metro_areas = top_n['Metro Area'].tolist()
outflow_variable = top_n[f'{migration_switch[migration_variable][5]}'].tolist()

# code to dynamically show top 5, top 4, etc. metros for the given county
if n>0:

    # sert the heading
    st.markdown(
    f"""
    <div style='margin-top: 20px; margin-bottom: 0px; text-align: center;'>
        <span style='font-size: 16px; font-weight: 200;'>
            Top Receiving Metros from {county} County (does not include {base_metro} metro):
        </span>
    </div>
    """,
    unsafe_allow_html=True)   

    # set columns dynamically based on unique metro areas (not including base metro)
    cols = st.columns(n)

    for i in range(n):
        cols[i].markdown(
            f"""
                <div style='margin-top: {margin_top}px; margin-bottom: {margin_bottom}px; text-align: center;'>
                    <div style='align-items: center;'><span style='font-size: 18px; font-weight: 700;'>{i+1}</span></div>
                    <span style='font-size: {font_size}px; font-weight: 200;'>
                        {metro_areas[i]}<br>{migration_switch[migration_variable][3]}{outflow_variable[i]:,}
                    </span>
                </div>
            """,
        unsafe_allow_html=True)
else:
    st.markdown(
        f"""
            <div style='margin-top: {margin_top}px; margin-bottom: {margin_bottom}px; text-align: center;'>
                <span style='font-size: 16px; font-weight: 200;'>
                    No counted migration from {county} County to outside the {base_metro} metro area (or rural areas).
                </span>
            </div>
        """,
            unsafe_allow_html=True)

# the custom CSS lives here:
hide_default_format = """
        <style>
            .reportview-container .main footer {visibility: hidden;}    
            #MainMenu, footer {visibility: hidden;}
            section.main > div:has(~ footer ) {
                padding-bottom: 1px;
                padding-left: 20px;
                padding-right: 20px;
                padding-top: 10px;
            }
            .stRadio [role=radiogroup]{
                align-items: center;
                justify-content: center;
            }
            [data-testid="stSidebar"] {
                padding-left: 10px;
                padding-right: 10px;
                padding-top: 0px;
                }
            [data-testid="stAppViewBlockContainer"] {
                padding-top: 23px;
                padding-left: 23px;
                }
            [class="stDeployButton"] {
                display: none;
            } 
            span[data-baseweb="tag"] {
                background-color: #737373 
                }
            div.stActionButton{visibility: hidden;}
        </style>
       """

# inject the CSS
st.markdown(hide_default_format, unsafe_allow_html=True)