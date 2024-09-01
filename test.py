import streamlit as st, pandas as pd, numpy as np, yfinance as yf
#import plotly.express as px
from datetime import datetime,timedelta
from datetime import date
#import matplotlib.pyplot as plt

st.title('Investing Aide')
st.caption('A Stock Dashboard to help you find all stock metrics and help with technical analysis')
ticker = st.sidebar.text_input('Ticker', 'AAPL')
today = datetime.today()
one_year_back = today - timedelta(days=371)
startDate = st.sidebar.date_input("Start Day (At least 1 Year Ago)", max_value=one_year_back)

endDate = st.sidebar.date_input('End Date (At Least 1 Year ahead of Start Date)')