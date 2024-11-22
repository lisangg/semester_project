# import libraries
import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import plotly.graph_objects as go

from datetime import datetime, timedelta
import re

# Page configuration
st.set_page_config(
    page_title="Stock Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded")

# CSS Styling

st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stMetricLabel"] {
  display: flex;
  font-weight: 900;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetric"] {
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricDelta"] svg {
    transform: translateX(40px);
    }
}

</style>
""", unsafe_allow_html=True)

# decorator @st.cache_data and @st.cache_resource 
#  store the results of expensive function calls and return the cached result when the same inputs occur again

@st.cache_resource
def load_ticker(symbol):
    ''' load ticker object from yfinance
    
    Args:
        symbol: ticker symbol for a stock, string
    
    Returns:
        ticker object
    '''
    return yf.Ticker(symbol)

@st.cache_data
def load_data(start_date, end_date, symbol):
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
    data.columns = ["Adj Close", "Close", "High", "Low", "Open", "Volume"]
    return data

@st.cache_data
def get_tickers_name():
    return pd.read_csv("nasdaq_screener.csv")["Symbol"]

def load_financial_data(ticker_object):
    financial_data = ticker_object.get_financials()
    financial_metrics = ticker_object.get_financials().index
    # split the string according to capitalize letters with preceding word character

    # (?<![A-Z\W])  what precedes is a word character EXCEPT for capital letters
    #(?=[A-Z])     and what follows is a capital letter

    financial_metrics = [re.sub(r'(?<![A-Z\W])(?=[A-Z])', ' ', metric) for metric in financial_metrics]    

    # replaced index with the new strings
    financial_data.index = financial_metrics
    return financial_data
    
def display_fundamental_data(ticker_object):
    
    # get the fundamental data about the ticker performance today
    metrics = ["previousClose", "open", "dayLow", "dayHigh"]
    labels = ["Previous Close", "Open", "Low", "High"]
    
    columns = st.columns(len(metrics))
    for (i, metric) in enumerate(metrics):
        with columns[i]:
            with st.container():
                st.metric(label=labels[i], value=ticker_object.info[metric])


# Visualizing functions

def display_line_graph(data):
    st.subheader("Closing Price")
    st.line_chart(data['Adj Close'], x_label='Date', y_label='Closing Price')

def display_candle_stick(data):
    
    # Plotting the candlestick chart with Plotly
    st.subheader("Candlestick Chart")
    fig = go.Figure(data=[go.Candlestick(x=data.index,
                                        open=data['Open'],
                                        high=data['High'],
                                        low=data['Low'],
                                        close=data['Adj Close'])])

    fig.update_layout(xaxis_title='Date', yaxis_title='Price')

    # Display the figure
    st.plotly_chart(fig)

def display_scatter_chart(symbol, data):
    st.scatter_chart(data, x='Volume', y='Close', x_label="Volume", y_label="Closing price")

def display_trading_volume(data):
    st.header("Trading Volume")
    st.line_chart(data['Volume'], x_label='Date', y_label='Volume')
    
def display_watch_list(watch_list):
## display watch list
# using session state
    with st.container():

        st.subheader("Your Watchlist")
        for stock in watch_list:
            with st.container(border=True):
                col1, col2 = st.columns(2)
                
                info = load_ticker(stock).info
                
                
                with col1:
                    st.write("")
                    st.write(info['shortName'])
                    st.subheader(stock)
                    
                with col2:
                    change = round(((info['open'] - info['previousClose'])/ info['previousClose']) * 100, 2)
                    st.metric("Open", info['open'], change)       

def display_financial_metric(financial_data, financial_metric):
    
    metric_data = financial_data.loc[financial_metric].rename_axis('Date').reset_index()
    metric_data['Year'] = [date.year for date in metric_data['Date']]

    st.bar_chart(data=metric_data, x='Year', y=financial_metric)

        
def display_download_options(data):
    # SEEING data and exporting option to csv file
    with st.expander('View Original Data'):
        st.dataframe(data, use_container_width=True)
        
        # st.download_button("Download Ticker Fundamental Data", data.to_csv(index=True), file_name=f"{symbol}_fundamental_data.csv", mime="text/csv")
        st.download_button("Download Historical Stock Data", data.to_csv(index=True), file_name=f"{symbol}_stock_data.csv", mime="text/csv")


######## PYTHON SCRIPT

# initialize a list for symbols in user watch list
# session state will store variables for each user session (values stay the same after rerun)

if 'watchlist' not in st.session_state:
    st.session_state['watchlist'] = []


# side bar
with st.sidebar:
    st.header("Settings")
    
    # select symbol
    symbol = st.selectbox("Select ticker symbol",
                          get_tickers_name())
    
    # allow user to add a stock to watch list
    if st.button("Add to watchlist"):
        if symbol not in st.session_state['watchlist']:
            st.session_state['watchlist'].append(symbol)
    
    # set date range
    min_date = datetime.strptime('01-01-2005', '%m-%d-%Y')
    max_date = datetime.today()
        
    # select date range
    start_date = st.date_input("Start date", min_date, min_value=min_date, max_value=max_date)
    end_date = st.date_input("End date", max_date, min_value=min_date, max_value=max_date)
    
    # load data for selected symbol and selected time range
    historical_data = load_data(start_date, end_date, symbol)
    ticker_object = load_ticker(symbol)
    financial_data = load_financial_data(ticker_object)

    # select chart type
    chart_selection = st.selectbox("Select a chart type", ("Line graph", "Candlestick"))
    
    financial_metric = st.selectbox("Select financial metric", financial_data.index)
    


# python script 

st.title("📈 Stock Dashboard")
st.subheader(f"Currently showing: {symbol}")

# show the fundamental data
display_fundamental_data(ticker_object)

# show chart according to user preference
if chart_selection == "Line graph":
    display_line_graph(historical_data)
else:
    display_candle_stick(historical_data)    

col1, col2 = st.columns([2,1])
# show trading volume
with col1:
    display_trading_volume(historical_data)
    
# show watch list
with col2:  
    display_watch_list(st.session_state["watchlist"]) 
    
display_download_options(historical_data)

# financials section
st.header('Financials')

# show financial data
st.subheader(f"Financial Metric: {financial_metric}")
display_financial_metric(financial_data, financial_metric)