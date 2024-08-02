"""Module we're using to run the app, explore data, and create visuals"""

import streamlit as st
import pandas as pd
import plotly.express as px

# Set the title and description for the app
st.title('Used Vehicle Sales Explorer')
st.write("""
This app performs simple explorations of used vehicle sales data.
- **Python libraries:** pandas, plotly.express, streamlit
- **Data source:** [Practicum content](https://practicum-content.s3.us-west-1.amazonaws.com/datasets/vehicles_us.csv)
""")

# Sidebar header for data filters
st.sidebar.header('Data filters')

@st.cache_data
def read_and_clean(path):
    """
    Preprocess the data from the CSV file.

    Parameters:
    - path: The path to the CSV file.

    Returns:
    - df: The cleaned DataFrame.
    """
    df = pd.read_csv(path)
    df = df.dropna(subset=['model_year'])
    df['model_year'] = pd.to_numeric(df['model_year'], errors='coerce').astype(int)
    df['date_posted'] = pd.to_datetime(df['date_posted'], format='%Y-%m-%d')
    df['make'] = df['model'].str.split(' ', expand=True)[0].astype('category')
    df = df.reset_index(drop=True)
    return df

# Preprocess the data
file_path = "vehicles_us.csv"
df_init = read_and_clean(file_path)

def selected_df(vehicles_df, selected_make, year):
    """
    Filter the DataFrame based on the selected year and manufacturer.

    Parameters:
    - vehicles_df: The input DataFrame to filter.
    - selected_make: The manufacturer selected from the dropdown or None.
    - year: The year selected from the dropdown or 'All'.

    Returns:
    - new_df: A filtered DataFrame based on the criteria.
    """
    if year == 'All' and not selected_make:
        new_df = vehicles_df
    elif year != 'All' and not selected_make:
        new_df = vehicles_df[vehicles_df['model_year'] == year]
    elif year != 'All' and selected_make:
        new_df = vehicles_df[(vehicles_df['model_year'] == year) & (vehicles_df['make'].isin(selected_make))]
    else:
        new_df = vehicles_df[vehicles_df['make'].isin(selected_make)]

    new_df = new_df.reset_index(drop=True)
    return new_df

# Sidebar - Create options for dropdown
options = list(reversed(range(1908, 2020)))
options_with_none = ['All'] + options

# Sidebar - Select the Year
selected_year = st.sidebar.selectbox('Model Year', options_with_none)

# Sidebar - Manufacturer selection
sorted_unique_makes = sorted(df_init['make'].unique())
selected_make = st.sidebar.multiselect('Manufacturer', sorted_unique_makes)

# Filter the data based on user selection
filtered_df = selected_df(df_init, selected_make, selected_year)

# Display data statistics
st.header('Display Stats of Selected Vehicle Data')
st.write("""
Select a year using the Data Filter. The resulting data for that year will appear below.
- **Please note:** selecting "All" will display the data for all years available.
""")
st.write("Number of results: ", filtered_df.shape[0])

# Display the DataFrame
st.write("Data Viewer")
table_df = filtered_df.astype(str)
st.dataframe(
    table_df,
    column_config={
         "model_year": st.column_config.NumberColumn(
            "model year",
            step=1,
            format="%d"
        ),
        "days_listed": st.column_config.NumberColumn(
            "days listed",
            step=1,
            format="$%d",
        )
    },
    hide_index=True,
)

# Data visualizations
st.header('Data Visualizations Exploring the Selected Year')
st.write("""
Please note: If the selected year yields no data, the charts will be blank.
""")

st.subheader('Introduction')
st.write("""
Going beyond a table, we can use data visualizations to give an overview of the information. Understanding the condition of the cars and
the average price by vehicle type can be helpful to both buyers and sellers in the used vehicle market.
""")

# Pie chart - Vehicle Conditions
condition_distribution = filtered_df['condition'].value_counts().reset_index()
condition_distribution.columns = ['condition', 'count']
fig_condition = px.pie(condition_distribution, values='count', names='condition', title='Distribution of Vehicle Conditions')
st.plotly_chart(fig_condition)

# Bar chart - Average Price by Vehicle Type
avg_price_by_type = filtered_df.groupby('type')['price'].mean().reset_index()
fig_price = px.bar(avg_price_by_type, x='type', y='price', title='Average Price by Vehicle Type')
st.plotly_chart(fig_price)

# Histogram - Vehicle Prices
st.subheader('Distribution of Vehicle Price by Condition')
st.write("""
The histogram of vehicle prices reveals the distribution of prices across the dataset.
This visualization helps identify the most common price ranges and any significant outliers.
""")
fig1 = px.histogram(filtered_df, x='price', nbins=50, color='condition', histnorm='percent', title='Vehicle Prices Distribution')
st.plotly_chart(fig1)

# Histogram - Compare Days Listed by Condition and Make
st.subheader('Comparison of Days Listed by Condition')
st.write("""
This histogram of days listed helps to visually compare the days listed for the selected manufacturers by condition.
Creating an expectation of how long a vehicle might be listed for helps buyers and sellers of used vehicles.
""")
normalize_histogram = st.checkbox('Normalize Histogram Data', value=False)
histnorm = 'probability' if normalize_histogram else ''
title = 'Normalized Distribution of Days Listed by Condition' if normalize_histogram else 'Distribution of Days Listed by Condition'
fig2 = px.histogram(filtered_df, x='days_listed', color='condition', histnorm=histnorm, title=title)
st.plotly_chart(fig2)

# Scatterplot: Price vs Odometer Reading
st.header('Price vs. Odometer Reading')
st.write("""
The scatterplot of price vs. odometer reading provides insights into how mileage affects the price of vehicles. Generally, we expect to see that higher mileage vehicles tend to be priced lower. This scatterplot helps validate or challenge that assumption and highlights any interesting patterns or anomalies in the data.
""")
fig3 = px.scatter(filtered_df, x='odometer', y='price', color='condition', title='Price vs. Odometer Reading', labels={'odometer': 'Odometer Reading', 'price': 'Price'})
st.plotly_chart(fig3)

# Insights and Conclusion
st.header('Insights')
st.write("""
### Conclusion
By analyzing the vehicle prices, days listed, and the relationship between price and odometer readings, we gain a better understanding of the used vehicle market dynamics. These visualizations can help both buyers and sellers make more informed decisions based on data-driven insights.
""")
