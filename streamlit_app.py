# import libraries
import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import plotly.graph_objects as go



from datetime import datetime, timedelta


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
def load_data(start_date='2005-01-01', end_date=datetime.today(), symbol='GOOGL'):
    # docStrings for a function is created with triple-quotation marks
    ''' download data for a specific ticker from yfinance library
    
    Args:
        start_date: represent the starting date, string
        end_date: represent the ending date, datetime object
        ticker: ticker symbol for a stock, string
    
    Returns:
        pandas dataframe consist of historical stock data for a specific stock
    '''

    # a function download data from yfinance
    
    data = yf.download(symbol, start_date, end_date)
    
    return data

@st.cache_data
def get_tickers_name():
    return pd.read_csv("nasdaq_screener.csv")["Symbol"]
        

# visualizing functions
def display_line_graph(symbol, data):
    st.subheader(F'{symbol} Closing Price')
    st.line_chart(data['Adj Close'], x_label='Date', y_label='Closing Price')

def display_candle_stick(symbol, data):
    
    # Plotting the candlestick chart with Plotly
    fig = go.Figure(data=[go.Candlestick(x=data.index,
                                        open=data['Open'][symbol],
                                        high=data['High'][symbol],
                                        low=data['Low'][symbol],
                                        close=data['Adj Close'][symbol])])

    fig.update_layout(title=f'{symbol} Candlestick Chart', xaxis_title='Date', yaxis_title='Price')

    # Display the figure
    st.plotly_chart(fig)
    




# retreieve default data 

data = load_data()





st.title("Stock Market Dashboard")


# SIDE BAR

with st.sidebar:
    st.header("Settings")
    
    min_date =  data.index.min().date()
    max_date = data.index.max().date()
    
    start_date = st.date_input("Start date", min_date, min_value=min_date, max_value=max_date)
    end_date = st.date_input("End date", max_date, min_value=min_date, max_value=max_date)
    time_frame = st.selectbox("Select time frame",
                              ("Daily", "Weekly", "Monthly", "Quarterly"),
    )
    chart_selection = st.selectbox("Select a chart type",
                                   ("Bar", "Area"))
    
    symbol = st.selectbox("Select ticker symbol",
                                   get_tickers_name())
    

data = load_data(start_date, end_date, symbol)


display_line_graph(symbol, data)
display_candle_stick(symbol, data)

# get the fundamental data about the ticker performance today
columns = ["previousClose", "open", "dayLow", "dayHigh"]

for col in columns:
    with st.container(border=True):
        st.write(ticker_object.info[col])
    

# SEEING data and exporting option to csv file
with st.expander('View Original Data'):
    st.dataframe(data)
    
    # st.download_button("Download Ticker Fundamental Data", data.to_csv(index=True), file_name=f"{symbol}_fundamental_data.csv", mime="text/csv")
    st.download_button("Download Historical Stock Data", data.to_csv(index=True), file_name=f"{symbol}_stock_data.csv", mime="text/csv")
