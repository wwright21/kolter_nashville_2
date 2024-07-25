import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_js_eval import streamlit_js_eval

# set year variables to be used in map layer
current_year = 2024
projected_year = 2029

# set page configurations
st.set_page_config(
    page_title="Kolter - Nashville",
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
    "<p style='text-align:center;color:#000000;'>Select metro Nashville county:</p>", 
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
        <span style='font-size: {title_font_size}px; font-weight: 700;'>Nashville Development Dashboard:</span>
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

# explanatory text dictionary
mappingVar_explanation = {
    'Total Population': '2024 estimate',
    'Senior Population': '2024 population estimate age 65 and over', 
    'Population Density': '2024 population per square mile',
    'Population Growth Rate': f'compound annual growth rate measuring the direction (either positive or negative) and magnitude of change in total population between the years {current_year} and {projected_year}',
    'Median Household Income': '2024 estimate',
    'Homeownership Growth Rate': f'compound annual growth rate measuring the direction (either positive or negative) and magnitude of change in total owner-occupied housing units between the years {current_year} and {projected_year}'
}

st.sidebar.markdown(
    f"<p style='text-align:center;color:#000000;font-size: 13px;'>*{mappingVar_explanation[attribute]}</p>", unsafe_allow_html=True
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
   'Flow of persons': ['people_net', 'People', '~s', ''],
    'Flow of dollars': ['agi_net', 'Adjusted Gross Income', '$~s', '$']
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

# Map dropdown to file paths
attribute_files = {
    'Total Population': f'Data/CSV/Color-coded maps - {current_year} Total Population.csv',
    'Senior Population': f'Data/CSV/Color-coded maps - {current_year} Senior Population.csv',
    'Population Density': f'Data/CSV/Color-coded maps - {current_year} Population Density.csv',
    'Population Growth Rate': f'Data/CSV/Color-coded maps - {current_year}-{projected_year} Growth Rate Population.csv',
    'Median Household Income': f'Data/CSV/Color-coded maps - {current_year} Median Household Income.csv',
    'Homeownership Growth Rate': f'Data/CSV/Color-coded maps - {current_year}-{projected_year} Growth Rate Owner Occ HUs.csv'
}

# Map dropdown to column names
attribute_columnNames = {
    'Total Population': f'{current_year} Total Population',
    'Senior Population': f'{current_year} Senior Population',
    'Population Density': f'{current_year} Population Density',
    'Population Growth Rate': f'{current_year}-{projected_year} Growth Rate: Population',
    'Median Household Income': f'{current_year} Median Household Income',
    'Homeownership Growth Rate': f'{current_year}-{projected_year} Growth Rate: Owner Occ HUs'
}

# Map dropdown to tooltip number formats
attribute_numberFormats = {
    'Total Population': lambda x: f"{x:,}",
    'Senior Population': lambda x: f"{x:,}",
    'Population Density': lambda x: f"{x:,.0f}",
    'Population Growth Rate': lambda x: f"{x * 100:.2f}%",
    'Median Household Income': lambda x: f"${x:,.0f}",
    'Homeownership Growth Rate': lambda x: f"{x * 100:.2f}%"  
}

# Map dropdown to colorbar number formats
attribute_colorbarFormats = {
    'Total Population': ',',
    'Senior Population': ',',
    'Population Density': ',',
    'Population Growth Rate': '.2%',
    'Median Household Income': '$,',
    'Homeownership Growth Rate': '.1%'  
}

# Map dropdown to choropleth colors
attribute_choroColor = {
    'Total Population': 'Blues',
    'Senior Population': 'Oranges',
    'Population Density': 'BuPu',
    'Population Growth Rate': 'Reds',
    'Median Household Income': 'Greens',
    'Homeownership Growth Rate': 'Purples'
}

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
attribute_df = load_attribute(attribute_files[attribute])
attribute_df['tooltip'] = attribute_df[attribute_columnNames[attribute]].apply(attribute_numberFormats[attribute])

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
    color=attribute_columnNames[attribute],
    color_continuous_scale=attribute_choroColor[attribute],
    custom_data=['tooltip', 'county_name'],
    labels={
        'tooltip': attribute_columnNames[attribute]
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
    colorbar_tickformat = attribute_colorbarFormats[attribute],
    colorbar_tickfont_size=12,
    colorbar_title_font_size=13,
    colorbar_orientation='h',
    colorbar_title_text=attribute_choroLegend[attribute],
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
st.write(" ")

# first, define a metro designation dictionary 
metro_clarification = {
    'Shelby County, TN': 'Shelby County, TN (Memphis metro)',
    'Montgomery County, TN': 'Montgomery County, TN (Clarkesville)',
    'Cook County, IL': 'Cook County, IL (Chicago metro)',
    'Knox County, TN': 'Knox County, TN (Knoxville metro)',
    'Loudon County, TN': 'Loudon County, TN (Knoxville metro)',
    'New York County, NY': 'New York County, NY (Manhattan)',
    'Hamilton County, TN': 'Hamilton County, TN (Chattanooga metro)',
    'Fulton County, GA': 'Fulton County, GA (Atlanta metro)',
    'Union County, NJ': 'Union County, NJ (NYC metro)',
    'Monmouth County, NJ': 'Monmouth County, NJ (NYC metro)',
    'Westchester County, NY': 'Westchester County, NY (NYC metro)',
    'Hudson County, NJ': 'Hudson County, NJ (NYC metro)',
    'Fairfield County, CT': 'Fairfield County, CT (NYC metro)',
    'San Mateo County, CA': 'San Mateo County, CA (Bay Area)',
    'Santa Clara County, CA': 'Santa Clara County, CA (Bay Area)',
    'Collier County, FL': 'Collier County, FL (Naples)',
    'Walton County, FL': 'Walton County, FL (Panhandle)',
    'Arlington County, VA': 'Arlington County, VA (D.C. metro)',
    'Morris County, NJ': 'Morris County, NJ (NYC metro)',
    'Lake County, IL': 'Lake County, IL (Chicago metro)',
    'Essex County, MA': 'Essex County, MA (Boston metro)',
    'DuPage County, IL': 'DuPage County, IL (Chicago metro)',
    'Palm Beach County, FL': 'Palm Beach County, FL (Miami metro)',
    'Broward County, FL': 'Broward County, FL (Miami metro)',
    'Albemarle County, VA': 'Albemarle County, VA (Charlottesville)',
    'Denton County, TX': 'Denton County, TX (Dallas-F.W. metro)',
    'Essex County, NJ': 'Essex County, NJ (NYC metro)',
    'King County, WA': 'King County, WA (Seattle metro)',
    'Moore County, NC': 'Moore County, NC (Pinehurst)',
    'Harris County, TX': 'Harris County, TX (Houston metro)',
    'Maricopa County, AZ': 'Maricopa County, AZ (Phoenix metro)',
    'Orange County, CA': 'Orange County, CA (L.A. metro)',
    'Jefferson County, AL': 'Jefferson County, AL (Birmingham metro)',
    'Kings County, NY': 'Kings County, NY (Queens)',
    'Travis County, TX': 'Travis County, TX (Austin metro)',
    'Jefferson County, KY': 'Jefferson County, KY (Louisville metro)',
    'Mecklenburg County, NC': 'Mecklenburg County, NC (Charlotte metro)',
    'Madison County, TN': 'Madison County, TN (Jackson)',
    'Orange County, FL': 'Orange County, FL (Orlando metro)',
    'DeKalb County, GA': 'DeKalb County, GA (Atlanta metro)',
    'Warren County, KY': 'Warren County, KY (Bowling Green)',
    'Madison County, AL': 'Madison County, AL (Huntsville metro)',
    'Hillsborough County, FL': 'Hillsborough County, FL (Tampa metro)',
    'Franklin County, OH': 'Franklin County, OH (Columbus metro)',
    'Clark County, NV': 'Clark County, NV (Las Vegas metro)',
    'Marion County, IN': 'Marion County, IN (Indianapolis metro)',
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
}

# inflow table xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
st.markdown(
    f"""
    <div style='margin-top: 20px; margin-bottom: 20px;'>
        <span style='font-size: 18px; font-weight: 700;'>Migration Inflow Summary Table (2018-2022):</span>
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

inflow_summary = inflow_summary.style.format(
    {
        "Inflow - AGI": lambda x: '${:,.0f}'.format(x),
        "AGI / Capita": lambda x: '${:,.2f}'.format(x)
    },
    thousands=','
)

st.dataframe(
    inflow_summary, 
    use_container_width=True, 
    height=200,
    )

# outflow table xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
st.markdown(
    f"""
    <div style='margin-top: 20px; margin-bottom: 20px;'>
        <span style='font-size: 18px; font-weight: 700;'>Migration Outflow Summary Table (2018-2022):</span>
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

outflow_summary = outflow_summary.style.format(
    {
        "Outflow - AGI": lambda x: '${:,.0f}'.format(x),
        "AGI / Capita": lambda x: '${:,.2f}'.format(x)
    },
    thousands=','
)

st.dataframe(
    outflow_summary, 
    use_container_width=True, 
    height=200,
    )

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