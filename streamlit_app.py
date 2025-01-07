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

# page configuration
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

## Data Functions

# decorator @st.cache_data and @st.cache_resource 
#  store the results of expensive function calls and return the cached result when the same inputs occur again

@st.cache_data
def get_tickers_name():
    ''' read a csv file containing stock symbols
    
    No Args:
    
    Returns:
        a list contain all stock symbols on nasdaq
    '''
    return pd.read_csv("nasdaq_screener.csv")["Symbol"]

@st.cache_resource
def load_ticker_object(symbol):
    ''' load ticker object from yfinance
    
    Args:
        symbol: ticker symbol for a stock, string
    
    Returns:
        ticker object
    '''
    return yf.Ticker(symbol)


def load_historical_data(ticker_object, start_date, end_date, interval):
    ''' download data for a specific ticker from yfinance library
    
    Args:
        ticker_object: ticker object from yfinance, Ticker object
        start_date: represent the starting date, string
        end_date: represent the ending date, datetime object
        interval: represent time interval of data, string
    
    Returns:
        pandas dataframe consist of historical stock data for a specific stock
    '''
    
    data = ticker_object.history(start=start_date, end=end_date, interval=interval)
    return data


def load_financial_data(ticker_object):
    ''' download data for a specific ticker from yfinance library
    
    Args:
        ticker_object: ticker object from yfinance, Ticker object
    
    Returns:
        pandas dataframe consist of the financials data for a specific stock
    '''
    financial_data = ticker_object.get_financials()
    financial_metrics = ticker_object.get_financials().index # "ReturnRevenue" or "EBIT"
    
    
    # split the string according to capitalize letters with preceding word character
    
    # using regular expression pattern
    # (?<![A-Z\W])  what precedes is a word character EXCEPT for capital letters
    #(?=[A-Z])     and what follows is a capital letter
    pattern = r'(?<![A-Z\W])(?=[A-Z])'
    
    # for each metric 
    # replace matching patterns with a space 
    financial_metrics = [re.sub(pattern, ' ', metric) for metric in financial_metrics]    

    # replaced index with the new formatted strings
    financial_data.index = financial_metrics
    
    return financial_data
    

# Display Functions

def display_fundamental_metrics(ticker_object):
    ''' output 4 metrics horizontally on streamlit webpage
    
    Args:
        ticker_object: ticker object from yfinance, Ticker object
    
    Returns:
        None
    '''
    
    metrics = ["previousClose", "open", "dayLow", "dayHigh"]
    labels = ["Previous Close", "Open", "Low", "High"]
    
    columns = st.columns(len(metrics))
    for (i, metric) in enumerate(metrics):
        with columns[i]:
            with st.container():
                st.metric(label=labels[i], value=ticker_object.info[metric])

## Graphing Functions

def display_line_graph(data):
    ''' output a line graph represent historical closing stock price of a specific stock
    
    Args:
        data: a dataframe containing stock price over time, pandas dataframe
    
    Returns:
        None
    '''
    
    st.subheader("Closing Price")
    st.line_chart(data['Close'], x_label='Date', y_label='Closing Price')
    


def display_candle_stick(data):
    ''' output a candle stick graph represent historical stock price of a specific stock
    
    Args:
        data: a dataframe containing stock price over time, pandas dataframe
    
    Returns:
        None
    '''
    
    # Plotting the candlestick chart with Plotly
    st.subheader("Candlestick Chart")
    fig = go.Figure(data=[go.Candlestick(x=data.index,
                                        open=data['Open'],
                                        high=data['High'],
                                        low=data['Low'],
                                        close=data['Close'])])

    fig.update_layout(xaxis_title='Date', yaxis_title='Price')

    # Display the figure
    st.plotly_chart(fig)

def display_trading_volume(data):
    ''' output a bar graph represent trading volume over time
    
    Args:
        data: a dataframe containing trading volume over time, pandas dataframe
    
    Returns:
        None
    '''
    
    st.header("Trading Volume")
    st.line_chart(data['Volume'], x_label='Date', y_label='Volume')
    
def display_watch_list(watch_list):
    
    ''' output a stock watchlist of stocks user add in one session
    
    Args:
        watch_list: contains a list of all the stocks added by user in one session, List
    
    Returns:
        None
    '''
    with st.container():

        st.subheader("Your Watchlist")
        for stock in watch_list:
            with st.container(border=True):
                col1, col2 = st.columns(2)
                
                info = load_ticker_object(stock).info
                
                
                with col1:
                    st.write("")
                    st.write(info['shortName'])
                    st.subheader(stock)
                    
                with col2:
                    change = round(((info['open'] - info['previousClose'])/ info['previousClose']) * 100, 2)
                    st.metric("Open", info['open'], change)       

def display_financial_metric(financial_data, financial_metric):
    ''' output a bar graph represent the financial metric for a stock over 4 years
    
    Args:
        data: a dataframe containing values of a metric over time, pandas dataframe
    
    Returns:
        None
    '''
    metric_data = financial_data.loc[financial_metric].rename_axis('Date').reset_index()
    metric_data['Year'] = [date.year for date in metric_data['Date']]

    st.bar_chart(data=metric_data, x='Year', y=financial_metric)

        
def display_download_options(data):
    ''' output an exander with download options on streamlit web application
    
    Args:
        data: a dataframe containing stock price over time, pandas dataframe
    
    Returns:
        None
    '''
    # SEEING data and exporting option to csv file
    with st.expander('View Original Data'):
        st.dataframe(data, use_container_width=True)
        
        st.download_button("Download Historical Stock Data", data.to_csv(index=True), file_name=f"stock_data.csv", mime="text/csv")



# initialize a list for symbols in user watch list
# session state will store variables for each user session (values stay the same after rerun)
if 'watchlist' not in st.session_state:
    st.session_state['watchlist'] = []
    

# side bar
with st.sidebar:
    st.header("Settings")
    
    # select symbol
    symbol = st.selectbox("Stock symbol",
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
    interval = st.selectbox("Time internval", ("1d", "5d", "1wk", "1mo", "3mo"))
    
    # load data for selected symbol and selected time range
    ticker_object = load_ticker_object(symbol)
    historical_data = load_historical_data(ticker_object, start_date, end_date, interval)
    financial_data = load_financial_data(ticker_object)

    # select chart type
    chart_selection = st.selectbox("Chart type", ("Line graph", "Candlestick"))
    
    financial_metric = st.selectbox("Financial metric", financial_data.index)
    
# display chart title and sub header
st.title("📈 Stock Dashboard")
st.subheader(f"Currently showing: {symbol}")

# display the fundamental data metrics for selected stock
display_fundamental_metrics(ticker_object)

# display chart according to user selection
if chart_selection == "Line graph":
    display_line_graph(historical_data)
else:
    display_candle_stick(historical_data)    

# create a two-column structure
col1, col2 = st.columns([2,1])

# display trading volume
with col1:
    display_trading_volume(historical_data)
    
# show watch list
with col2:  
    display_watch_list(st.session_state["watchlist"]) 
    
# display the expander for download option
display_download_options(historical_data)

# display header for financials section
st.header('Financials')

# display bar graph for financial data
st.subheader(f"Financial Metric: {financial_metric}")
display_financial_metric(financial_data, financial_metric)