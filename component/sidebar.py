# SIDEBAR-YEAR        
import streamlit as st
import numpy as np   
def show_sidebar(df):
    
    min_released_year = df['released_year'].min()
    max_released_year = df['released_year'].max()

    st.sidebar.write("Select year range:")
    year_range = st.sidebar.slider("Year range:", min_released_year, max_released_year, (min_released_year, max_released_year))
    
    col_sb_month, col_sb_day = st.columns(2)
    
    with col_sb_month:
        # SIDEBAR-MONTH 
        month_name_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        sb_month_name = st.sidebar.selectbox("Month:", month_name_list, 0)
        
        sb_month = month_name_list.index(sb_month_name) + 1
        print("Select Month:",sb_month)
        
    # with col_sb_day:
    #     # SIDEBAR-DAY
    #     sb_day = st.sidebar.selectbox("Day:", range(1,32), 0)
    #     print("Select Day:",sb_day)

    
    # SIDEBAR-MODE show unique data from df column 'mode'
    sb_mode = st.sidebar.selectbox("Mode:", df['mode'].unique())
    
    sb_key = st.sidebar.selectbox("Key:", np.sort(df['key'].unique()))
    
    
    # show data based on sidebar selection
    # df = df[(df['released_year'] >= year_range[0]) & (df['released_year'] <= year_range[1])]
    #based on mode
    df = df[df['mode'] == sb_mode]