import random
import copy
import csv
import math
import time
import statistics
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import numpy as np


class Stock():
  def __init__(self, name,dump):
    self.name = name
    self.avglength=[]
    self.medlength=[]
    self.ratios=[]
    self.fdim_mean=0
    self.fdim_median=0
    self.list_val=dump #list of attributes, in case of stock a list(close,volume,volatility) in same order as time

class Test():
  def __init__(self):
    self.avglength=[]
    self.medlength=[]
    self.list_val={} #list of attributes, in case of stock a list(close,volume,volatility) in same order as time


def dist(a,b,tpsize):
	d=abs(a-b)
	return round(d,5)

def mean_val(b1,time,tpsize):
  tnew=tpsize*(time+1)
  tprev=tpsize*(time)
  
  navg=0
  pavg=0
  for i in range(0,tpsize):
    navg+=(float)(b1.list_val['close'][tnew+i])
    pavg+=(float)(b1.list_val['close'][tprev+i])

  navg/=tpsize
  pavg/=tpsize

  return dist(navg,pavg,tpsize)

def floatify(l):
	newl=[]
	for i in l:
		newl.append((float)(i))
	return newl

def med_val(b1,time,tpsize):
  tnew=tpsize*(time+1)
  tprev=tpsize*(time)

  navg=(statistics.median(floatify(b1.list_val['close'][tnew:tnew+tpsize])))
  pavg=(statistics.median(floatify(b1.list_val['close'][tprev:tprev+tpsize])))

  navg/=tpsize
  pavg/=tpsize

  return dist(navg,pavg,tpsize)

def readStocks():
  bdict={}
  with open('allstocks.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    prev="AAPL"
    open1=[]
    close=[]
    low=[]
    high=[]
    volume=[]
    dataMap=[]
    temp=[]
    for data in csv_reader:
        if data[2].endswith("2014") or data[2].endswith("2015") or data[2].endswith("2016") or data[2].endswith("2017"):
            if prev==data[1]:
                open1.append(data[3])
                volume.append(data[7])
                high.append(data[4])
                low.append(data[5])
                close.append(data[6])
            
            else:
                temp={}
                temp['name']=prev
                temp['open']=open1
                temp['volume']=volume
                temp['high']=high
                temp['low']=low
                temp['close']=close
                #print(temp)
                dataMap.append(temp)
                bdict[prev]=temp
                #print(dataMap)
                open1=[]
                volume=[]
                high=[]
                low=[]
                close=[]
                temp=[]
                prev=data[1]
                open1.append(data[3])
                volume.append(data[7])
                high.append(data[4])
                low.append(data[5])
                close.append(data[6])
      
  return bdict


def length(s,tpsize,n):
	limit=n//tpsize
	time=1
	avg_len=0
	med_len=0
	for time in range(1,limit):
		avg_len+=mean_val(s,time,tpsize)
		med_len+=med_val(s,time,tpsize)

	return (avg_len,med_len)


def setlengths(los,tpsize,n):
	for s in los:
		(mean,median)=length(s,tpsize,n)
		s.medlength.append(round(math.log(median),2))
		s.avglength.append(round(math.log(mean),2))

	return los

def calc_fd(s):
	mean=[]
	median=[]
	avgl=s.avglength
	medl=s.medlength
	n=len(avgl)

	for i in range(0,n-1):
		for j in range(i+1,n):
			mean.append((avgl[i]-avgl[j])/(i-j))
			median.append((medl[i]-medl[j])/(i-j))

	s.fdim_mean=(statistics.median(avgl))
	s.fdim_median=(statistics.median(medl))

	return s

def cluster(los):
	l=[]
	
	for s in los:
		l.append([s.fdim_mean,s.fdim_median])

	X = np.array(l)
	kmeans = KMeans(n_clusters=5, random_state=0).fit(X)
	print(kmeans.labels_)

def simulate(n,sizes, stno,logsc):
	los=[]
	sdict=readStocks()
	for s in sdict:
		temp= Stock(s,sdict[s])
		los.append(temp)

	for l in sizes:
		los=setlengths(los,l,n)

	for s in los:
		s=calc_fd(s)
		print(s.name,"      ",s.fdim_mean)

	cluster(los)


	plt.plot(logsc,los[stno].avglength, 'ro')
	plt.axis([0, 7, 0, 10])
	plt.show()
	x=[]
	y=[]
	for s in los:
		x.append(s.fdim_mean)
		y.append(s.fdim_median)

	#plt.plot(x,y, 'ro')
	#plt.axis([0,6,0,4])
	#plt.show()


attributes={
	'n':800,
	'scales':[1,2,4,8,16,32,64,128],
	'logscales':[0,1,2,3,4,5,6,7],
  'stock':25
}

simulate(attributes['n'],attributes['scales'],attributes['stock'],attributes['logscales'])








