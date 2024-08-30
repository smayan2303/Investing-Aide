import appdirs as ad
ad.user_cache_dir = lambda *args: "/tmp"
import streamlit as st, pandas as pd, numpy as np, yfinance as yf
import plotly.express as px
from datetime import datetime,timedelta
from datetime import date
from alpha_vantage.fundamentaldata import FundamentalData
from stocknews import StockNews

st.title('Stock Dashboard')
ticker = st.sidebar.text_input('Ticker', 'MSFT')
today = datetime.today()
one_year_back = today - timedelta(days=371)
startDate = st.sidebar.date_input("Start Day (At least 1 Year Ago)", max_value=one_year_back)

endDate = st.sidebar.date_input('End Date (At Least 1 Year ahead of Start Date)')

data = yf.download(ticker)


data = data.loc[startDate:endDate].copy()



fig = px.line(data, x = data.index, y = data["Adj Close"], title = ticker)
st.plotly_chart(fig)

pricing_data, fundamental_data, news, Gemini, tech_indicator = st.tabs(['Pricing Data', 'Fundamental Data', 'Top 10 News', 'Gemini: AI Analysis', 'Technical Analysis Dashboard'])

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






with fundamental_data:
    st.write('fundamental data')

    

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
    st.subheader('Technical Analysis Dashboard:')
    df = pd.DataFrame()
    ind_list = df.ta.indicators(as_list=True)
    #st.write(ind_list)
    technical_indicator = st.selectbox('Tech Indicator', options=ind_list)
    method = technical_indicator
    indicator = pd.DataFrame(getattr(ta,method)(low = data['Low'], close=data['Close'], high=data['High'], open=data['Open'], volume = data['Volume']))
    indicator['Close'] = data['Close']
    fig2 = px.line(indicator, title = ticker)
    st.plotly_chart(fig2)
    st.write(indicator)