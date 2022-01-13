import pandas as pd
import numpy as np
import datetime as dt
import yfinance as yf
import INDICATORS
import matplotlib.pyplot as plt

stocks =['RELIANCE.NS','LT.NS','BAJFINANCE.NS','INFY.NS','SBIN.NS']


start = dt.datetime.today()-dt.timedelta(days=40)
end = dt.datetime.today()

Ril= yf.download(stocks[0],start,end,interval='15m')
indicator=INDICATORS.TechnicalIndicators(Ril)

y=pd.DataFrame()
pd.concat([Ril,indicator.EMA_Double(Ril,20,50)],axis=1)

y=Ril.iloc[49:,:].copy(deep=True)
z=pd.DataFrame(columns=['Date','Position','Price']) 


#======================================================
        #BACKTESTING
#======================================================
signal=""
returns=[]
y['ret']=None



for i in range(1,len(y.index)):
    
    if signal == "":
        returns.append(float(0))
        y.ret[i]=float(0)
        if (y.EMA_20[i-1] < y.EMA_50[i-1]) and \
            (y.EMA_20[i] >= y.EMA_50[i]):
                
                signal = "BUY"
                z=z.append({'Date':y.index[i],'Position':signal,'Price':y.Close[i]},ignore_index=True)
                
        if (y.EMA_20[i-1] >= y.EMA_50[i-1]) and \
            (y.EMA_20[i] < y.EMA_50[i]):
                
                signal = "SELL"
                z=z.append({'Date':y.index[i],'Position':signal,'Price':y.Close[i]},ignore_index=True)

        
                
                
    elif signal == 'BUY':
        
        if (y.EMA_20[i-1] >= y.EMA_50[i-1]) and \
            (y.EMA_20[i] < y.EMA_50[i]):
                
                signal = "SELL"
                z=z.append({'Date':y.index[i],'Position':signal,'Price':y.Close[i]},ignore_index=True)

                
        else:
            
            returns.append((y.Close[i]/y.Close[i-1])-1)
            y.ret[i]= float((y.Close[i]/y.Close[i-1])-1)
            
    elif signal == 'SELL':
        
        if (y.EMA_20[i-1] < y.EMA_50[i-1]) and \
            (y.EMA_20[i] >= y.EMA_50[i]):
                
                signal = "BUY"
                z=z.append({'Date':y.index[i],'Position':signal,'Price':y.Close[i]},ignore_index=True)

                
        else:
            returns.append((y.Close[i-1]/y.Close[i])-1)
            y.ret[i]= float((y.Close[i-1]/y.Close[i])-1)

            
y.ret.isnull().value_counts()        
y.ret.fillna(float(0.0),inplace=True)

y['compund']=(1+y.ret).cumprod()

volatility(y.compund)
CAGR(y.compund)
max_dd(y.compund)
sharpe(y.compund,0.05)
                
        
        
    
    
for i in z.Date:
    print(i)
    print(y.index[i])
    

    








#---------------------------------------------------------------
def CAGR(DF):
    "function to calculate the Cumulative Annual Growth Rate of a trading strategy"
    df = DF.copy()
    n = len(df)/(252*78)
    CAGR = (df[-1])**(1/n) - 1
    return CAGR

def volatility(DF):
    "function to calculate annualized volatility of a trading strategy"
    df = DF.copy()
    vol = df.std() * np.sqrt(252*78)
    return vol

def sharpe(DF,rf):
    "function to calculate sharpe ratio ; rf is the risk free rate"
    df = DF.copy()
    sr = (CAGR(df) - rf)/volatility(df)
    return sr
    

def max_dd(DF):
    "function to calculate max drawdown"
    df = DF.copy()
    l={}
    l["cum_roll_max"] = df.cummax()
    l["drawdown"] = l["cum_roll_max"] - df
    l["drawdown_pct"] = l["drawdown"]/l["cum_roll_max"]
    max_dd = l["drawdown_pct"].max()
    return max_dd


