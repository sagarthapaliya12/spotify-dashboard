import streamlit as st
from streamlit.logger import get_logger

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns

LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="Spotify Dashboard",
        page_icon=":musical_note:",
    )

    st.header("Spotify 2023 Dashboard")

    st.sidebar.success("Select a demo above.")

    st.markdown(
        """
        The following table is the preview of the dataframe used to build the spotify dashboard.
    """
    )
    
    # @st.cache_data
    def load_data():
        file_path = 'resources/spotify2023.pkl'
        return pd.read_pickle(file_path)

    df = load_data()

# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    #dataset preview
    with st.expander("Data Preview"):
        st.dataframe(df)

    #showing top 10 most streamed song
    top_10 = df.nlargest(10, "streams")[["track_name", "streams"]]

    # One song's name is too long, change it to a shorter version
    top_10.loc[top_10["track_name"] == "Sunflower - Spider-Man: Into the Spider-Verse", "track_name"] = "Sunflower: Into the Spider-Verse"
    
    st.subheader("Top 10 Most streamed songs")
    # Divide streams column by billions for easier understanding
    top_10["streams"] = top_10["streams"].div(1000000000)
    top_10_sorted = top_10.sort_values(by='streams')
    # Create a visualisation
    plt.figure(figsize = (10,5))
    plt.xticks(rotation=45, ha = "right")
    plt.ticklabel_format(style='plain', axis='both', scilimits=(0,0))
    st.bar_chart(data = top_10_sorted, x = "track_name", y = "streams")
    plt.xlabel("Track name")
    plt.ylabel("Streams - billion")
    plt.show()

    def create_scatter_plot(data, x_variables):
        scatter_plots = []

        for var in x_variables:
            scatter_plot = px.scatter(data, x=var, y='streams', title=f'Streams vs. {var}')
            scatter_plots.append(scatter_plot)

        return scatter_plots
    
    

    # List of variables for scatter plots
    variables = ["bpm", "danceability", "valence", "energy", "acousticness", "instrumentalness", "liveness", "speechiness"]

    scatter_plots = create_scatter_plot(data=df, x_variables=variables)

    # Display the grid of scatter plots in Streamlit
    st.subheader("Scatter Plots")

    num_plots = len(scatter_plots)
    rows = (num_plots // 3) + (num_plots % 3 > 0)  # Calculate the number of rows

    for row in range(rows):
        cols = st.columns(3)
        for col in range(3):
            idx = row * 3 + col
            if idx < num_plots:
                with cols[col]:
                    st.plotly_chart(scatter_plots[idx], use_container_width=True)

#

if __name__ == "__main__":
    run()