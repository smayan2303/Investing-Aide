import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pandas_datareader as data
import yfinance as yf
from datetime import datetime,timedelta
from datetime import date
import streamlit as st


st.title('Stock Trend Moving Average Predictor')

today = datetime.today()
one_year_back = today - timedelta(days=371)
ticker_input = st.text_input('Enter Stock Ticker', 'AAPL')
Startday_input = st.date_input("Choose a starting day for the data(At least 1 Year Ago)", max_value=one_year_back)




today = today.strftime("%Y %m %d")

df = yf.download(ticker_input)


df = df.loc[Startday_input.strftime("%Y %m %d"):today].copy()
df['% Change'] = (df['Adj Close'] / df['Adj Close'].shift(1) - 1) * 100

st.subheader('Data and Metrics')
x = st.dataframe(data = df, width = 1000)


st.subheader('Closing Price vs Time')
fig = plt.figure(figsize = (12,6))
ax1 = fig.add_subplot(111, ylabel='Price in $',  xlabel='Date')
plt.plot(df.Close)
plt.title(ticker_input + ' Closing Price')
st.pyplot(fig)

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
plt.title(ticker_input + ' Closing Price and Simple Moving Averages')
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
plt.title(ticker_input + ' Closing Price and Exponential moving Averages')
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


#Todo:
#Show the metrics used and their values for the current stock and Moving Average Timelines
#Also add a briefdescription of each value under it with st.caption

