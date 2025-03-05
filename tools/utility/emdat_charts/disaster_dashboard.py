import streamlit as st
import pandas as pd
import plotly.express as px

# Enable caching for data loading
@st.cache_data
def load_data():
    df = pd.read_excel("emdat_2025.xlsx", sheet_name="EM-DAT Data")
    # Pre-calculate decade for later use
    df['Decade'] = (df['Start Year'] // 10) * 10
    return df

# Cache filtered dataframe
@st.cache_data
def filter_data(df, years, disaster_type, country):
    mask = (df['Start Year'] >= years[0]) & (df['Start Year'] <= years[1])
    if disaster_type != 'All':
        mask = mask & (df['Disaster Type'] == disaster_type)
    if country != 'All':
        mask = mask & (df['Country'] == country)
    return df[mask]

# Cache aggregation operations
@st.cache_data
def get_time_series(df, col='count'):
    if col == 'count':
        return df.groupby('Start Year').size().reset_index(name='count')
    return df.groupby('Start Year')[col].sum().reset_index()

@st.cache_data
def get_top_countries(df, n=10):
    return df['Country'].value_counts().head(n).reset_index()

# Set page config
st.set_page_config(page_title="Natural Disasters Dashboard", layout="wide")

try:
    # Load data once
    df = load_data()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    min_year = int(df['Start Year'].min())
    max_year = int(df['Start Year'].max())
    selected_years = st.sidebar.slider(
        "Select Year Range", 
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )
    
    # Use lists instead of sets for faster operations
    countries = ['All'] + sorted(df['Country'].unique().tolist())
    selected_country = st.sidebar.selectbox("Select Country", countries)
    
    disaster_types = ['All'] + sorted(df['Disaster Type'].unique().tolist())
    selected_type = st.sidebar.selectbox("Select Disaster Type", disaster_types)
    
    # Filter data once
    filtered_df = filter_data(df, selected_years, selected_type, selected_country)
    
    # Create visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        disasters_by_year = get_time_series(filtered_df)
        fig1 = px.line(disasters_by_year, x='Start Year', y='count',
                       title=f'Number of Disasters Over Time {f"in {selected_country}" if selected_country != "All" else ""}')
        st.plotly_chart(fig1, use_container_width=True)
        
        deaths_by_year = get_time_series(filtered_df, 'Total Deaths')
        fig3 = px.line(deaths_by_year, x='Start Year', y='Total Deaths',
                       title=f'Total Deaths Over Time {f"in {selected_country}" if selected_country != "All" else ""}')
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        if selected_country == 'All':
            top_countries = get_top_countries(filtered_df)
            top_countries.columns = ['Country', 'Count']
            fig2 = px.bar(top_countries, x='Country', y='Count',
                         title='Top 10 Most Affected Countries')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            type_dist = filtered_df['Disaster Type'].value_counts().reset_index()
            type_dist.columns = ['Disaster Type', 'Count']
            fig2 = px.bar(type_dist, x='Disaster Type', y='Count',
                         title=f'Disaster Types in {selected_country}')
            st.plotly_chart(fig2, use_container_width=True)
    
    # Summary metrics (calculated once)
    total_disasters = len(filtered_df)
    total_deaths = filtered_df['Total Deaths'].fillna(0).sum()
    total_affected = filtered_df['Total Affected'].fillna(0).sum()
    total_damage = filtered_df['Total Damage, Adjusted (\'000 US$)'].fillna(0).sum()
    
    st.header("Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Disasters", f"{total_disasters:,}")
    col2.metric("Total Deaths", f"{total_deaths:,.0f}")
    col3.metric("Total Affected", f"{total_affected:,.0f}")
    col4.metric("Total Damage (USD)", f"${total_damage:,.0f}k")
    
    # Only show detailed country analysis if a country is selected
    if selected_country != 'All':
        st.header(f"Top 5 Deadliest Disasters in {selected_country}")
        deadliest = filtered_df.nlargest(5, 'Total Deaths')[
            ['Start Year', 'Disaster Type', 'Total Deaths', 'Total Affected']
        ]
        st.dataframe(deadliest, use_container_width=True)
    
    # Show smaller sample of detailed data
    st.header("Recent Disasters")
    display_cols = [
        'Country', 'Disaster Type', 'Start Year', 
        'Total Deaths', 'Total Affected', 'Total Damage, Adjusted (\'000 US$)'
    ]
    st.dataframe(
        filtered_df[display_cols].sort_values('Start Year', ascending=False).head(100),
        use_container_width=True
    )

except Exception as e:
    st.error(f"Error loading or processing the data: {str(e)}")
    st.write("Please make sure the Excel file 'emdat_2025.xlsx' is in the same directory as this script.")