import streamlit as st
import pandas as pd
import plotly.express as px

st.title('Used Vehicle Sales Explorer')

st.write("""
This app performs simple explorations of used vehicle sales data.  
- **Python libraries:** pandas, plotly.express, streamlit  
- **Data source:** [Practicum content](https://practicum-content.s3.us-west-1.amazonaws.com/datasets/vehicles_us.csv)
""")

st.sidebar.header('Data filters')

@st.cache_data

def read_and_clean(file_path):
    # Read in the file
    df = pd.read_csv(file_path)

    # Tidy the data
    # Drop rows without a year 
    df = df.dropna(subset=['model_year'])

    df['is_4wd'] = df['is_4wd'] == 1.0
    df['date_posted'] = pd.to_datetime(df['date_posted'],format='%Y-%m-%d')

    # Change date_posted from object to datetime
    columns_to_fill = ['odometer', 'cylinders', 'paint_color']

    for column in columns_to_fill:
        if column == 'paint_color':
            df[column] = df[column].fillna('unknown')
        else:
            df[column] = df[column].fillna(0.0)

    # Convert model_year column to int
    df['model_year'] = df['model_year'].astype('int')

    # Create a 'make' column for manufacturer
    df['make'] = df['model'].str.split(' ', expand=True)[0]
    df['make'] = df['make'].astype('category')

    vehicles_df = df.reset_index()
    return vehicles_df

# Preprocess the data
file_path = "vehicles_us.csv"
vehicles_df = read_and_clean(file_path)

# Function to filter and show data for the selected year
def filtered_df(vehicles_df, selected_make, selected_year='All'):
    """
    Filter the DataFrame based on the selected year and manufacturer.
    
    Parameters:
    - df: The input DataFrame to filter.
    - selected_year: The year selected from the dropdown or 'all'.
    - selected_manufacturer: The manufacturer selected from the dropdown or None.

    Returns:
    - A filtered DataFrame based on the criteria.
    """
    if selected_year == 'All' and not selected_make:
        # Show all the data
        filtered_df = vehicles_df
    elif selected_year != 'All' and not selected_make:
        # Filter by year only
        filtered_df = vehicles_df[vehicles_df['model_year'] == selected_year]
    elif selected_year != 'All' and selected_make:
       # Filter by year and make 
       filtered_df = vehicles_df[(vehicles_df['model_year'] == selected_year) & (vehicles_df['make'].isin(selected_make))]
    else:
        # If the year is 'all' and a manufacturer is selected
        #filtered_df = vehicles_df[(vehicles_df['Manufacturer'] == selected_make)]
        filtered_df = vehicles_df[(vehicles_df.make.isin(selected_make))]

    return filtered_df
    

# Sidebar - Create options for dropdown
options = list(reversed(range(1908, 2020)))
options_with_none = ['All'] + options

# Sidebar - Select the Year
selected_year = st.sidebar.selectbox('Model Year', options_with_none)

# Sidebar - Manufacturer selection
sorted_unique_makes = sorted(vehicles_df.make.unique())
selected_make = st.sidebar.multiselect('Manufacturer', sorted_unique_makes)
#df_selected_make = vehicles_df[(vehicles_df.make.isin(selected_make))]

filtered_df = filtered_df(vehicles_df, selected_make, selected_year)


# Display data
st.header('Display Stats of Selected Vehicle Data')
st.write("""
Select a year using the Data Filter. The resulting data for that year will appear below. 
- **Please note:** selecting "All" will display the data for all years available.
""")
st.write("Number of results: ", filtered_df.shape[0])


# Display the dataframe based on the selected year
st.data_editor(
    filtered_df,
    column_config={
        "model_year": st.column_config.NumberColumn(
            "model year",
            format="%f"
        ),
        "paint_color":st.column_config.Column(
            "paint color"
        ),
        "days_listed":st.column_config.Column(
            "days listed"
        ),
        "is_4wd":st.column_config.Column(
            "has 4wd"
        ),
        "date_posted": st.column_config.DateColumn(
            "date posted",
            format="MM-DD-YYYY",
            step=1,
        ),
    },
    hide_index=True,
)


st.write(' ')
st.write(' ')
st.write(' ')


st.header('Data Visualizations Exploring the Selected Year')
st.write("""
    Please note: If the selected year yields no data, the charts will be blank.
""")


st.write(' ')
st.write(' ')
st.write(' ')


st.subheader('Introduction')
st.write("""
    Going beyond a table, we can use the data visualizations to give an overview of the information. Understanding the condition of the cars and
    the average price by vehicle type can be helpful to both buyers and sellers in the used vehicle market.
""")


# Distribution of vehicle condition
condition_distribution = filtered_df['condition'].value_counts().reset_index()
condition_distribution.columns = ['condition', 'count']

# Pie chart - Vehicle Conditions
fig_condition = px.pie(condition_distribution, values='count', names='condition', title='Distribution of Vehicle Conditions')
st.plotly_chart(fig_condition)


# Bar chart - Average Price by Vehicle Type 
# Average price by vehicle type
avg_price_by_type = filtered_df.groupby('type')['price'].mean().reset_index()

# Create a bar chart of vehicle prices by type
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


# Histogram - Compare Days Listed by Condiiton and Make
st.subheader('Comparison of Days Listed by Condition')
st.write("""
This histogram of days listed helps to visually compare the days listed for the selected manufacturers by condition.
Creating an expectation of how long a vehicle might be listed for helpful to buyers and sellers of used vehicles. 
         """)

# Checkbox - Normalize data for histogram
normalize_histogram = st.checkbox('Normalize Histogram Data', value=False)


if normalize_histogram:
    histnorm = 'probability'
    title = 'Normalized Distribution of Days Listed by Condition'

else:
    histnorm = ''
    title = 'Distribution of Days Listed by Condition'


fig2 = px.histogram(filtered_df, x='days_listed', color='condition', histnorm=histnorm, title=title)
st.plotly_chart(fig2)





# Scatterplot: Price vs Odometer Reading
st.header('Price vs. Odometer Reading')
st.write(""" 
The scatterplot of price vs. odometer reading provides insights into how mileage affects the price of vehicles. Generally, we expect to see that higher mileage vehicles tend to be priced lower. This scatterplot helps validate or challenge that 
assumption and highlights any interesting patterns or anomalies in the data.  
""")
fig3 = px.scatter(filtered_df, x='odometer', y='price', color='condition', title='Price vs. Odometer Reading', labels={'odometer':'Odometer Reading', 'price':'Price'})
st.plotly_chart(fig3)


st.write(' ')
st.write(' ')
st.write(' ')

# Insights and Conclusion
st.header('Insights')
st.write("""
### Conclusion
By analyzing the vehicle prices, days listed, and the relationship between price and odometer readings, we gain a better understanding of the used vehicle market dynamics. These visualizations can help both buyers and sellers make more informed decisions based on data-driven insights.
""")