import streamlit as st
from streamlit.logger import get_logger

import altair as alt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import plotly.graph_objects as go

LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="Spotify Dashboard",
        page_icon=":musical_note:",
    )

    
    
    @st.cache_data
    def load_data():
        file_path = 'resources/spotify2023.pkl'
        return pd.read_pickle(file_path)

    df = load_data()

# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
 

   # Get or set the session state
    if "search_input" not in st.session_state:
        st.session_state["search_input"] = ""

    # Create a sidebar with a search input and a search button
    search_input = st.sidebar.text_input("Search for an artist or track", value= st.session_state.search_input)
    
    search_button = st.sidebar.button("Search")

    if search_button:
        search_input = search_input.lower()

        # Check if the input is a track name or artist name
        if search_input in df['track_name'].str.lower().values or search_input in df['artist_name'].str.lower().values:
            # Filter the dataframe based on the search input
            filtered_df = df[(df['artist_name'].str.lower().str.contains(search_input)) | (df['track_name'].str.lower().str.contains(search_input))]

            if not filtered_df.empty:
                # Sort the dataframe in decreasing order of streams
                sorted_df = filtered_df.sort_values('streams', ascending=False)
                # Display the dataframe
                st.header(f"Search results for '{search_input}'")
                st.subheader(f"Each Song Details of {search_input}")
                st.dataframe(sorted_df)

                # Create a spider plot for the searched artist in the sorted dataframe
                features = ["danceability", "valence", "energy", "acousticness", "instrumentalness", "liveness", "speechiness"]

                # INSTEAD OF PASSING MANUALLY THE FEATURES, WE CAN DO IT LIKE THIS
                
                mean_features = filtered_df[features].mean()
                print(mean_features[0])
                    
                # Create a spider plot
                fig = go.Figure(data=go.Scatterpolar(
                    r=mean_features,
                    theta=features,
                    fill='toself'
                ))

                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]                        
                        )),
                    showlegend=False,
                    height=600,                         
                )
                st.header(f"Feature of songs of {search_input}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("No results found for your search.")
        else:
             st.write("Please enter a valid search query.")
    else:
        st.header("Spotify 2023 Dashboard")

        st.markdown(
            """
            The following table is the preview of the DataFrame used to build the spotify dashboard.
        """
        )
        #dataset preview
        with st.expander("Data Preview"):
            st.dataframe(df)

        # Create two columns
        col1, col2 = st.columns(2)

        # Showing top 10 most streamed song in the first column
        with col1:
            st.subheader("Top 10 Most streamed songs on Spotify")

            top_10 = df.nlargest(10, "streams")[["track_name", "streams"]]
           
            top_10.loc[top_10["track_name"] == "Sunflower - Spider-Man: Into the Spider-Verse", "track_name"] = "Sunflower: Into the Spider-Verse"

            top_10["streams"] = top_10["streams"].div(1000000000)

            plt.figure(figsize = (8,6))
            plt.xticks(rotation=45, ha = "right")
            plt.ticklabel_format(style='plain', axis='both', scilimits=(0,0))
            plot = sns.barplot(data = top_10, x = "track_name", y = "streams", color="#00A36C")
            plt.xlabel("Track name")
            plt.ylabel("Streams - billion")    
            st.pyplot(plot.get_figure())

        # Which artists has the most streamed songs in the second column
        with col2:
            st.subheader("Artists with the most streams on Spotify")

            played = df.groupby("artist_name")["streams"].agg("sum").sort_values(ascending=False)
            most_played = played.nlargest(10)
            plt.figure(figsize = (8,6))
            plt.xticks(rotation=45, ha = "right")
            plot = sns.barplot(x = most_played.index, y = (most_played/1000000000), color="#ffaa00")
            plt.xlabel("Artist")
            plt.ylabel("Streams - billion")
            st.pyplot(plot.get_figure())
            pass

            
        # Sort the dataframe by 'streams' and take the top 10
        st.subheader("Distribution of Top 10 Songs Across Various Music Charts")
        top_songs = df.sort_values('streams', ascending=False).head(10)

            # Melt the dataframe to long format
        melted_df = pd.melt(top_songs, id_vars=['track_name'], value_vars=['in_apple_charts', 'in_shazam_charts', 'in_spotify_charts', 'in_deezer_charts'])

            # Create a stacked column chart
        chart = alt.Chart(melted_df).mark_bar().encode(
                x='track_name:N',
                y='value:Q',
                color='variable:N',
                tooltip=['track_name', 'variable', 'value']
          )

        
        st.altair_chart(chart, use_container_width=True)

        #Scatter Plot to show different Visualizations
        st.subheader("Scatter Plot to visualize different characteristics")

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