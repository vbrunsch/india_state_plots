import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize
import datetime
'''
numdays=100
base = datetime.date.today()
date_list = [base - datetime.timedelta(days=x) for x in range(numdays)]
print(base)
print(date_list)
'''
def linear_fit(x, a, b):
    return  a*x+b

pop= {"Andaman and Nicobar Islands":434192, "Andhra Pradesh":90959737, "Arunachal Pradesh":1382611, 
      "Assam":35607039, "Bihar":104099452, "Chandigarh":1169000, "Chhattisgarh":29436231, 
      "Dadra and Nagar Haveli and Daman and Diu":585764, "Goa":1458545, "Gujarat":60439692,
      'Haryana':25351462, 'Himachal Pradesh':7451955, 'Jammu and Kashmir':13606320, 
      'Jharkhand':38471, 'Karnataka':67562686, 'Kerala':35699443, 'Ladakh':274289, 
      'Lakshadweep':64473, 'Madhya Pradesh':85047748, 'Maharashtra':
112374333, 'Manipur':2855794, 'Meghalaya':3366710, 'Mizoram':1239244, 'Nagaland':1980602, 
      'Odisha':47645822, 'Puducherry':877010, 'Punjab':30141373, 'Rajasthan':81032689, 
      'Sikkim':619000, 'Tamil Nadu':77841267, 'Telangana':38510982, 'Tripura':4071, 
      'Uttar Pradesh':237882725, 'Uttarakhand':11250858, 'West Bengal':100580953, "Delhi":31181000}
df = pd.read_csv('https://prsindia.org/covid-19/cases/download')
df['Year'] = df['Date'].apply(lambda x : int(x.split('/')[2]))
df = df[df['Year'] > 2019] # filter out rows with year = 1970,...etc
df['Date'] = pd.to_datetime(df.Date, dayfirst=True)


for item in list(pop.keys())[:15]:
    state = item # can choose any state from df.Region.unique()
    threshold = 20 # x cases per million population
    offset_days = 60 # keep the most recent 60 days
    days = [(45,60)] # the time window to fit the decline curve, 45-60 usually works (60 is the most recent date)
    try:
        focus = df[df['Region'] == state].set_index('Date', drop=True)
        focus.index = pd.to_datetime(focus.index).strftime('%y/%m/%d')
        focus = focus['Confirmed Cases'].diff()[-offset_days:] 
        title = state
        fig, ax = plt.subplots(nrows=1, ncols=1, sharey=True, figsize=(16,9))
        ax.plot(focus.index, focus.values, alpha=0.3)#, label=r'Daily cases in %s'%title)
        ax.plot(focus.rolling(window=7, min_periods=1, center=True).mean(), c='green',alpha=0.3, ls='--')    
        for i,(a,b) in enumerate(days):
            slope, intercept = optimize.curve_fit(linear_fit, np.arange(a,b), np.log(focus.values[a:b]+1))[0]
            #print(np.arange(a,b))
            ax.plot(np.arange(a,b), np.exp(np.arange(a,b)*slope + intercept), c=('C'+str(i+1)))
            ax.annotate(np.round(np.exp(slope),3), xy=((a+b-2)/2, np.exp((a+b+2)/2*slope + intercept)), fontsize=24, c=('C'+str(i+1)))
        #ax.set_yscale('log') #turn on/off this line to use log or linear scale

        b = np.array([focus.values[-1]])

        while b[-1] > pop[state] / 1e6 * threshold :
            b = np.append(b, b[-1]*(1+slope))
        numdays=len(b)+10
        base = datetime.date.today()
        #pd.to_datetime(focus.index).strftime('%y/%m/%d')                                                                                    
        date_list = list(focus.index)+[(base + datetime.timedelta(days=x)).strftime('%y/%m/%d')  for x in range(0+numdays)]
        #print(date_list)                                                                                                                    
        ax.plot(date_list,[threshold for x in range(0,len(date_list))],'--', label='1/Mppl', linewidth=2)
        ax.legend(prop={'size': 30})
        ax.tick_params(labelsize=20)
        ax.xaxis.set_major_locator(plt.MaxNLocator(8))
        ax.set_ylim(bottom=1, )    
        ax.plot(np.arange(len(focus),len(focus)+len(b)), b, ls='-.', c='C4')
        ax.annotate(s=str(len(b))+' days until \ndaily cases\n<'+str(threshold)+' /Mppl', xy=(len(focus)+len(b)-9, 10), fontsize=20, ha='center', c='C4')
        plt.title(state, fontsize=20)
        plt.tight_layout()
        plt.savefig(state+'_2.png')
    except:
        print(item)
        continue
