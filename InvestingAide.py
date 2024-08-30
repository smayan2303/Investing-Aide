import streamlit as st, pandas as pd, numpy as np, yfinance as yf
import plotly.express as px
from datetime import datetime,timedelta
from datetime import date
from alpha_vantage.fundamentaldata import FundamentalData
from stocknews import StockNews
import matplotlib.pyplot as plt
import pandas_datareader as data




st.title('Investing Aide')
st.caption('A Stock Dashboard to help you find all stock metrics and help with technical analysis')
ticker = st.sidebar.text_input('Ticker', 'AAPL')
today = datetime.today()
one_year_back = today - timedelta(days=371)
startDate = st.sidebar.date_input("Start Day (At least 1 Year Ago)", max_value=one_year_back)

endDate = st.sidebar.date_input('End Date (At Least 1 Year ahead of Start Date)')

data = yf.download(ticker)


data = data.loc[startDate:endDate].copy()



fig = px.line(data, x = data.index, y = data["Adj Close"], title = ticker)
st.plotly_chart(fig)

MA_and_Buy_Rating, pricing_data, news, Gemini, tech_indicator = st.tabs(['Moving Averages and Buy Ratings','Pricing Data', 'Recent News', 'Gemini: AI Analysis', 'Technical Analysis'])

with pricing_data:
    st.header("Price Movements")
    data2 = data
    data2['% Change'] = (data['Adj Close'] / data['Adj Close'].shift(1) - 1) * 100
    #st.write(data2)
    st.dataframe(data = data2, width = 1000)
    annual_return = (data['Adj Close'].iloc[-1] / data['Adj Close'].iloc[-252] - 1) * 100
    st.write('Annual return is ',annual_return,'%')

    stdev = np.std(data2['% Change'])*np.sqrt(252)
    st.write('Standard Deviation is ',stdev,'%')
    st.write('Risk Adjusted Return is ',annual_return/stdev)






with MA_and_Buy_Rating:
    df = data
    df['% Change'] = (df['Adj Close'] / df['Adj Close'].shift(1) - 1) * 100

    
    longMA_input = st.slider('Enter the LONGER term moving average time frame for the SMA'   , min_value=10, max_value=200, value=50, step=1)
    shortMA_input = st.slider('Enter the SHORTER term moving average time frame for the SMA'   , min_value=5, max_value=150, value=21, step=1)

    SMAupper = int(longMA_input) 
    SMAlower = int(shortMA_input)

    st.subheader('Closing Price and Simple Moving Averages vs Time')
    df['maLow'] = df.Close.rolling(SMAlower).mean()
    df['maHigh'] = df.Close.rolling(SMAupper).mean()
    fig = plt.figure(figsize = (12,6))
    ax1 = fig.add_subplot(111, ylabel='Price in $',  xlabel='Date')
    df['Close'].plot(ax=ax1)
    df['maLow'].plot(ax=ax1, color='g')
    df['maHigh'].plot(ax=ax1, color='r')


    df['SMAbullish'] = 0.0
    df['SMAbullish'] = np.where(df['maLow'] > df['maHigh'], 1.0, 0.0)
    df['SMAcrossover'] = df['SMAbullish'].diff()


    ax1.plot(df.loc[df.SMAcrossover == 1.0].index, 
            df.Close[df.SMAcrossover == 1.0],
            '^', markersize=10, color='g')
    ax1.plot(df.loc[df.SMAcrossover == -1.0].index, 
            df.Close[df.SMAcrossover == -1.0],
            'v', markersize=10, color='r')
    shortSMA = 'SMA ' + str(SMAlower)
    longSMA = 'SMA ' + str(SMAupper)
    plt.legend(['Close', shortSMA, longSMA, 'Buy', 'Sell'])
    plt.title(ticker + ' Closing Price and Simple Moving Averages')
    st.pyplot(fig)


    longEMA_input = st.slider('Enter the LONGER term exponential moving average time frame for the EMA'   , min_value=10, max_value=200, value=50, step=1)
    shortEMA_input = st.slider('Enter the SHORTER term exponential moving average time frame for the EMA'   , min_value=5, max_value=150, value=21, step=1)

    EMAupper = int(longEMA_input) 
    EMAlower = int(shortEMA_input)



    st.subheader('Closing Price and Exponential Moving Averages vs Time')
    df['ema_short'] = df['Close'].ewm(span=EMAlower, adjust=False).mean()
    df['ema_long'] = df['Close'].ewm(span=EMAupper, adjust=False).mean()

    fig = plt.figure(figsize = (12,6))
    ax1 = fig.add_subplot(111, ylabel='Price in $',  xlabel='Date')
    df['Close'].plot(ax=ax1)
    df['ema_short'].plot(ax=ax1, color='g')
    df['ema_long'].plot(ax=ax1, color='r')


    df['EMAbullish'] = 0.0
    df['EMAbullish'] = np.where(df['ema_short'] > df['ema_long'], 1.0, 0.0)
    df['EMAcrossover'] = df['EMAbullish'].diff()


    ax1.plot(df.loc[df.EMAcrossover == 1.0].index, 
            df.Close[df.EMAcrossover == 1.0],
            '^', markersize=10, color='g')
    ax1.plot(df.loc[df.EMAcrossover == -1.0].index, 
            df.Close[df.EMAcrossover == -1.0],
            'v', markersize=10, color='r')

    shortEMA = 'EMA ' + str(EMAlower)
    longEMA = 'EMA ' + str(EMAupper)
    plt.legend(['Close', shortEMA, longEMA, 'Buy', 'Sell'])
    plt.title(ticker + ' Closing Price and Exponential moving Averages')
    st.pyplot(fig)



    SMAdistancePercent = df['maLow'].iloc[-1] / df['maHigh'].iloc[-1]
    SMAdistancePercentFactor = SMAdistancePercent / 1.15


    EMAdistancePercent = df['ema_short'].iloc[-1] / df['ema_long'].iloc[-1]
    EMAdistancePercentFactor = EMAdistancePercent / 1.1


    PriceTrend = 0
    if(df['Close'].iloc[-252] < df['Close'].iloc[-1]):
        PriceTrend += 0.25
    if(df['Close'].iloc[-126] < df['Close'].iloc[-1]):
        PriceTrend += 0.25
    if(df['Close'].iloc[-28] < df['Close'].iloc[-1]):
        PriceTrend += 0.25
    if(df['Close'].iloc[-5] < df['Close'].iloc[-1]):
        PriceTrend += 0.25



    dy = np.gradient(df['ema_short'])
    EMALowTrend = 0

    if(dy[-1] > dy[-5]):
        EMALowTrend += 0.4
    if(dy[-1] > dy[-28]):
        EMALowTrend += 0.3
    if(dy[-1] > dy[126]):
        EMALowTrend += 0.2
    if(dy[-1] > 0):
        EMALowTrend += 0.1



    dySMA = np.gradient(df['maLow'])
    SMALowTrend = 0

    if(dySMA[-1] > dySMA[-5]):
        SMALowTrend += 0.4
    if(dySMA[-1] > dySMA[-28]):
        SMALowTrend += 0.3
    if(dySMA[-1] > dySMA[126]):
        SMALowTrend += 0.2
    if(dySMA[-1] > 0):
        SMALowTrend += 0.1



    currentBelowShorter = 0
    if(df['Close'].iloc[-1] > df['maLow'].iloc[-1]):
        currentBelowShorter += 0.5

    if(df['Close'].iloc[-1] > df['ema_short'].iloc[-1]):
        currentBelowShorter += 0.5



    currentBelowLonger = 0
    if(df['Close'].iloc[-1] > df['maHigh'].iloc[-1]):
        currentBelowLonger += 0.5

    if(df['Close'].iloc[-1] > df['ema_long'].iloc[-1]):
        currentBelowLonger += 0.5



    FinalStockRating = SMAdistancePercentFactor * 0.2 + EMAdistancePercentFactor * 0.2 + PriceTrend * 0.2 + SMALowTrend * 0.1 + EMALowTrend * 0.1 + currentBelowShorter * 0.1 + currentBelowLonger * 0.1


    buyRating = str(round(FinalStockRating * 100, 3)) + "%"



    st.write(f"<h1 style='color:white; text-align: center;'>{"The Buy Rating is: "}</h1>", unsafe_allow_html=True)
    if(FinalStockRating >= 0.5):
        st.write(f"""<div style='text-align: center; color: green; font-size: 4em; '>{buyRating}</div>""", unsafe_allow_html=True)
    else:
        st.write(f"""<div style='text-align: center; color: red; font-size: 4em; font-weight:bold'>{buyRating}</div>""", unsafe_allow_html=True)

    
import requests
from bs4 import BeautifulSoup

with news:
    news_ticker = yf.Ticker(ticker)
    news = news_ticker.news

    for article in news:
        st.subheader(f"{article['title']}")
        st.write(f"Publisher: {article['publisher']}")
        st.write(f"Link: {article['link']}")
        st.write(f"<div style='margin-bottom: 40px'></div>", unsafe_allow_html=True)



from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('API_KEY')

import google.generativeai as genai

genai.configure(api_key=os.getenv('API_KEY'))

model = genai.GenerativeModel('gemini-1.5-flash')
response1 = model.generate_content(f"3 Reasons to Buy {ticker} Stock(Do not include the disclaimer")
response2 = model.generate_content(f"3 Reasons to Sell {ticker} Stock(Do not include the disclaimer")
response3 = model.generate_content(f"SWOT Analysis of {ticker} stock")
with Gemini:
    buy_reason, sell_reason, swot_analysis = st.tabs(['3 Reasons to Buy', '3 Reasons to Sell', 'SWOT Analysis'])

    with buy_reason:
        st.write(response1.text)

    with sell_reason:
        st.write(response2.text)

    with swot_analysis:
        st.write(response3.text)

import pandas_ta as ta

with tech_indicator:
    st.subheader('Technical Analysis Interface:')
    df = pd.DataFrame()
    ind_list = df.ta.indicators(as_list=True)
    #st.write(ind_list)
    technical_indicator = st.selectbox('Tech Indicator', options=ind_list, placeholder = 'bbands')
    method = technical_indicator
    indicator = pd.DataFrame(getattr(ta,method)(low = data['Low'], close=data['Close'], high=data['High'], open=data['Open'], volume = data['Volume']))
    indicator['Close'] = data['Close']
    fig2 = px.line(indicator, title = ticker)
    st.plotly_chart(fig2)
    st.write(indicator)