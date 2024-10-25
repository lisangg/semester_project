# import libraries
import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from datetime import datetime, timedelta



st.title("Stock Market Dashboard")

# decorator @st.cache_data and @st.cache_resource 
#  store the results of expensive function calls and return the cached result when the same inputs occur again

@st.cache_resource
def load_ticker(ticker='MSFT'):
    ''' load ticker object from yfinance
    
    Args:
        ticker: ticker symbol for a stock, string
    
    Returns:
        ticker object
    '''
    return yf.Ticker(ticker)

@st.cache_data
def load_data(start_date = '2000-01-01', end_date = datetime.today().strftime('%Y-%m-%d'), ticker='GOOGL'):
    # docStrings for a function is created with triple-quotation marks
    ''' download data for a specific ticker from yfinance library
    
    Args:
        start_date: represent the starting date in %Y-%m-%d format, string
        end_date: represent the ending date in %Y-%m-%d format, string
        ticker: ticker symbol for a stock, string
    
    Returns:
        pandas dataframe consist of historical stock data for a specific stock
    '''

    # a function download data from yfinance
    
    data = yf.download(ticker,start_date, end_date)
    
    return data

data = load_data()
st.write(data)

# ticker = load_ticker()

# SIDE BAR

with st.sidebar:
    st.title("YouTube Channel Dashboard")
    st.header("⚙️ Settings")
    
    max_date = data.index.max().date()
    default_start_date = max_date - timedelta(days=365)  # Show a year by default
    default_end_date = max_date
    start_date = st.date_input("Start date", default_start_date, min_value=data.index.min().date(), max_value=max_date)
    end_date = st.date_input("End date", default_end_date, min_value=data.index.min().date(), max_value=max_date)
    time_frame = st.selectbox("Select time frame",
                              ("Daily", "Weekly", "Monthly", "Quarterly"),
    )
    chart_selection = st.selectbox("Select a chart type",
                                   ("Bar", "Area"))

# VISUALIZATIONS
# st.subheader("Closing Price")
# st.line_chart(data['Adj Close'])

# st.subheader("Volume Price")
# st.line_chart(data['Volume'])
