import streamlit as st
from streamlit.logger import get_logger
from component.metrics import show_metrics
import component.sidebar as sb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px

LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="Spotify Dashboard",
        page_icon="🎵",
        layout="wide",
    )

    st.write("## Spotify-2023 Dashboard!")
  
    @st.cache_data
    def load_data():
        return pd.read_pickle('rsc\spotify2023.pkl')

    df = load_data()
    
    
    sb.show_sidebar(df)
    
    #Main Window
    
    with st.expander("Data Preview"):
        st.dataframe(df)
    
    tab1, tab2, tab3 = st.tabs(["Data Metrics", "Data Comparison", "Song Analysis"])
    
    with tab1:
          
        # show metrics
        show_metrics(df)
        

        # show ttitle with a margin
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)


        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Top 10 Tracks")
            grouped_df = df.groupby('track_name')['streams'].sum().reset_index()
            sorted_df = grouped_df.sort_values('streams', ascending=False).head(10)

            chart = alt.Chart(sorted_df).mark_bar().encode(
                x='streams',
                y=alt.Y('track_name', sort='-x',title='Track'),
            ).properties(
                width=600,
                height=400
            )
            st.altair_chart(chart)
        with col2:
            st.subheader("Top 10 Artists")
            df['artist_name'] = df['artist_name'].str.split(',')
            df = df.explode('artist_name')

            df['artist_name'] = df['artist_name'].str.strip()

            # Group by artist_name and count unique track_name entries
            grouped_df = df.groupby('artist_name')['track_name'].nunique().reset_index()

            
            sorted_df = grouped_df.sort_values('track_name', ascending=False).head(10)

            chart = alt.Chart(sorted_df).mark_bar().encode(
                y=alt.Y('artist_name', sort='-x', title='Artist', axis=alt.Axis(labelOverlap=True)),
                x=alt.X('track_name', title='track'),
                
            ).properties(
                width=600,
                height=400
            )
            st.altair_chart(chart)
        
            
        st.subheader("Top Charts")
        
        with st.container(border=True):
            st.subheader("Spotify")
            grouped_df = df.groupby('track_name').agg({'in_spotify_charts': 'sum', 'in_spotify_playlists': 'sum', 'streams': 'sum'}).reset_index()

            non_zero_grouped_df = grouped_df[grouped_df['in_spotify_charts'] > 0]

            sorted_df = non_zero_grouped_df.sort_values('in_spotify_charts', ascending=True)
            sorted_df = sorted_df[sorted_df['in_spotify_charts'] == 1]

            melted_df = sorted_df.melt(id_vars='track_name', value_vars=['streams', 'in_spotify_playlists'])
            
            #stacked bar chart
            chart = alt.Chart(melted_df).mark_bar().encode(
                x=alt.X('value', scale=alt.Scale(type='log'), title='Value (Log Scale)'),
                y=alt.Y('track_name', sort='-x', title='Track'),
                color='variable',
                tooltip=['track_name', 'variable', 'value']
            ).properties(
                width=1000,
                height=500
            )
            st.altair_chart(chart)
    
    with tab2:

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
            ).properties(
                height=600
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
                        
                        
    with tab3:
        search_input = st.text_input("Search for an artist or track")
    
        search_button = st.button("Search")

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
        
    
if __name__ == "__main__":
    run()
