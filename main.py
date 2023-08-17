
import yaml
from yaml.loader import SafeLoader
with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static

#InsertDataFrame
excel_file = "C:/Users/anpark/PycharmProjects/streamlit/Data/County_Data.xlsx"
sheet_name = 'CountyData'

df = pd.read_excel(
    excel_file,
    sheet_name=sheet_name,
    header=0,
    usecols='A:Q')

# Folium map
#Authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status == False:
    st.error("Username/Password is incorrect")

if authentication_status is None:
    st.warning("Please enter your username and password")

if authentication_status:
    #InsertDataFrame
    excel_file = "C:/Users/anpark/PycharmProjects/streamlit/Data/County_Data.xlsx"
    sheet_name = 'CountyData'

    df = pd.read_excel(
        excel_file,
        sheet_name=sheet_name,
        header=0,
        usecols='A:Q')

    #SIDEBAR
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome {name}")
    st.sidebar.image("data/Logo CoreLogic2023red (1).png")
    st.sidebar.header("Please Filter Here: ")
    def get_default_county(selected_state):
        # Filter the county options based on the selected state
        filtered_county_options = df[df["State"] == selected_state]["County"].unique()
        return [filtered_county_options[0]] if filtered_county_options.size > 0 else None

    # Get the selected state from the state multiselect
    selected_state = st.sidebar.multiselect(
        "Select the State:",
        options=df["State"].unique(),
        default=df["State"].unique()
    )

    default_county = get_default_county(selected_state[0]) #Set the default county based on the selected state

    # Store the selected state and its default county in st.session_state
    if "selected_state" not in st.session_state:
        st.session_state.selected_state = selected_state[0]
        st.session_state.default_county = default_county

    # Check if the selected state has changed
    if st.session_state.selected_state != selected_state[0]:
        # Update the default county for the new selected state
        st.session_state.selected_state = selected_state[0]
        st.session_state.default_county = get_default_county(selected_state[0])

    county = st.sidebar.multiselect(
        "Select the County:",
        options=df[df["State"] == st.session_state.selected_state]["County"].unique().tolist(),
        default=[st.session_state.default_county[0]] if st.session_state.default_county else None
    )

    df_selection = df.query(
        "State == @selected_state & County == @county"
    )

    #Page 1: Login and Map
    #MainDashboard
    st.title("FLV County Dashboard")

    #Map&Login
    required = df_selection["Login Required"]
    login = df_selection["User Id"]
    password = df_selection["Password"]

    column1, column2, column3, column4 = st.columns(4)
    with column1:
        st.info("County Website:")
        for url in df_selection["URL"]:
            st.write(f"[County Recorder Link]({url})")

    with column2:
        st.info("Login Required: ")
        for index, login_required in enumerate(df_selection["Login Required"]):
            st.write(f" {login_required}")

    with column3:
        st.info("User ID: ")
        for index, user_id in enumerate(df_selection["User Id"]):
            st.write(f"{user_id}")

    with column4:
        st.info("Password: ")
        for index, password_info in enumerate(df_selection["Password"]):
            st.write(f"{password_info}")

    #Folium map
    m = folium.Map(location=[38, -96.5], zoom_start=4, scrollWheelZoom=False, tiles='CartoDB Positron', name="Test Map")

    us_test = f"./test.csv"
    us_data = pd.read_csv(us_test)

    choices = ['Average Total Fee']
    choice_select = st.selectbox("Select choice", choices)

    folium.Choropleth(
        geo_data='./us-state-boundaries.geojson',
        name="Choropleth",
        data=us_data,
        columns=["State Code", choice_select],
        key_on="feature.properties.state",
        fill_color= "Oranges",
        fill_opacity=0.7,
        #line_opacity=.1,
    ).add_to(m)

    #folium.features.GeoJson('us-state-boundaries.geojson', name="States", popup=folium.features.GeoJsonPopup(field=["basename"])).add_to(m)

    folium_static(m, width=700, height=500)

    st.markdown("---")
    ############################################################################

    #TopKPIS
    average_tier = round(df_selection["Tier"].mean(), 1)
    star_rating = ":star:" * int(round(average_tier, 0))
    average_access = round(df_selection["Access Fee"].mean(), 1)
    average_image = round(df_selection["Image Fee"].mean(), 1)
    average_charge = round(df_selection["Additional Charge"].mean(), 1)
    notes = (df_selection["Notes"])
    fips_code = int(df_selection["Fips"].mean())

    one_column, two_column, three_column, four_column, five_column = st.columns(5)
    with one_column:
        st.info('Access Fee: ')
        st.metric(label="Period", value=f"${average_access:,.0f}")
    with two_column:
        st.info('Image Fee: ')
        st.metric(label="Doc/Page", value=f"${average_image:,}")
    with three_column:
        st.info('Extra Fee: ')
        st.metric(label="Transaction Fee", value=f"${average_charge:,}")
    with five_column:
        st.info('Tier: ')
        st.subheader(f"{average_tier}  {star_rating}")
    with four_column:
        st.info('Fips: ')
        st.metric(label="FIPS Code", value=f"{fips_code:}")

    # BarChart
    bars_columns = ["Access Fee", "Image Fee", "Additional Charge"]
    label_columns = ['Period', 'Doc/Page', 'Page']

    # Filter the DataFrame based on the selected counties
    df_selection = df[df["County"].isin(county)]
    # Plotting the grouped bar chart using Plotly
    fig = go.Figure()

    #colors = ['#5A5A5A', '#FF4B4B', '#FAFAFA']  # custom colors for bar graph

    for county in df_selection["County"].unique():
        county_df = df_selection[df_selection["County"] == county]
        bar_values = county_df[bars_columns].sum()
        fig.add_trace(go.Bar(
            x=label_columns,
            y=bar_values,
            name=county,
            #marker_color=colors
        )
    )

    # Customize the layout of the grouped bar chart
    fig.update_layout(barmode='group', title='County Access Prices', xaxis_title='Labels', yaxis_title='Values',
                          title_x=.41)

    # Display the grouped bar chart using Streamlit with reduced widget size
    st.plotly_chart(fig)
    st.warning("Please verify if there are duplicates. If so, please use the dataframe below to confirm information.")
    st.markdown("---")
    ###############################################################################################

    #TierRules
    st.subheader("Tier Rules")
    st.text("Tier 1: All required documents exist within CoreLogic's recording image database or can be obtained at no cost"
            "\nTier 2: Additional manual effort is necessary to obtain required documents from official recorder's and only requires a document fee"
            "\nTier 3: Additional manual effort (beyond Tier 1 & 2) to obtain required documents and requires Document and Access Fee"
            "\nTier 4: Abstractor document retrieval required")

    #NotesColumn
    st.subheader('Important Notes:')
    for county in df_selection["County"].unique():
        notes = df_selection[df_selection["County"] == county]["Notes"]
        for note in notes.dropna():
            st.warning(f"{county}: {note}")

    st.dataframe(df_selection)
