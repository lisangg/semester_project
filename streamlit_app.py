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

def display_fundamental_data(ticker_object):
    
    # get the fundamental data about the ticker performance today
    metrics = ["previousClose", "open", "dayLow", "dayHigh"]
    
    columns = st.columns(len(metrics))
    for (i, metric) in enumerate(metrics):
        with columns[i]:
            with st.container(border=True):
                st.metric(label=metric, value=ticker_object.info[metric])
               

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
    
def display_watch_list():
## display watch list
# using session state
    with st.container(border=True):

        st.subheader("Your Watchlist")
        for stock in st.session_state['watchlist']:
            with st.container(border=True):
                col1, col2 = st.columns(2)

                try:
                    profitMargins = load_ticker(symbol).info['profitMargins']
                except KeyError:
                    profitMargins = "N/A"
                    
                    
                with col1:
                    st.write(load_ticker(symbol).info['shortName'])
                    st.write(symbol)
                
                with col2:    
                    st.write(profitMargins)

                    if profitMargins >= 0:
                        # change the color to green
                        pass
                    else:
                        # chanage the color to red
                        pass
                

# Initialization
if 'watchlist' not in st.session_state:
    st.session_state['watchlist'] = []

# retreieve default data 

data = load_data()


st.title("Stock Market Dashboard")


# SIDE BAR
def display_sidebar():
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
        
def display_download_options():
    # SEEING data and exporting option to csv file
    with st.expander('View Original Data'):
        st.dataframe(data)
        
        # st.download_button("Download Ticker Fundamental Data", data.to_csv(index=True), file_name=f"{symbol}_fundamental_data.csv", mime="text/csv")
        st.download_button("Download Historical Stock Data", data.to_csv(index=True), file_name=f"{symbol}_stock_data.csv", mime="text/csv")


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
                                   ("Line graph", "Candlestick"))
        
    symbol = st.selectbox("Select ticker symbol",
                          get_tickers_name())
    
    # allow user to add a stock to watch list
    if st.button("Add to watchlist"):
        if symbol not in st.session_state['watchlist']:
            st.session_state['watchlist'].append(symbol)
             

data = load_data(start_date, end_date, symbol)
ticker_object = load_ticker()

display_fundamental_data(ticker_object)

if chart_selection == "Line graph":
    display_line_graph(symbol, data)
else:
    display_candle_stick(symbol, data)
    
    
display_watch_list()    
display_download_options()



                
                    


