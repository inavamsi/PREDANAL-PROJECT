import random
import copy
import csv
import math
import time
import statistics

class Bird():
  def __init__(self, name,dump, boardsize):
    self.dir=normalize(2*random.random()-1,2*random.random()-1)
    self.speed = round(random.random(),4)
    self.x = random.randint(0,boardsize)
    self.y = random.randint(0,boardsize)
    self.name = name
    self.list_val=dump #list of attributes, in case of stock a list(close,volume,volatility) in same order as time
    self.history=[]
    self.nbr={}

def normalize(u,v):
  if u==0 and v==0:
    return (0,0)
  nu=u/math.sqrt(u*u+v*v)
  nv=v/math.sqrt(v*v+u*u)
  return (round(nu,4),round(nv,4))

def dist(x1,y1,x2,y2,boardsize):

  xs1=(x1-x2)*(x1-x2)
  ys1=(y1-y2)*(y1-y2)

  xs2=(boardsize-abs(x1-x2))*(boardsize-abs(x1-x2))
  ys2=(boardsize-abs(y1-y2))*(boardsize-abs(y1-y2))

  xs=min(xs1,xs2)
  ys=min(ys1,ys2)

  dist=math.sqrt(xs+ys)
  return dist

def bdist(b1,b2, boardsize):
  x1=b1.x
  y1=b1.y
  x2=b2.x
  y2=b2.y
  return dist(x1,y1,x2,y2, boardsize)

def randomly(arr):
  if(arr==[]):
    return None                                    
  n=len(arr)
  r=random.random()
  for i in range(0,n):
    if(r<(i+1)/n):
      return arr[i]
  return arr[n-1]

#move in direction
def move_vector(x,y,direction,speed):
  (u,v)=direction
  if u==0 and v==0:
    return (u,v)
  r = random.random()
  directions=[(1,0),(0,1),(-1,0),(0,-1)]
  d=randomly(directions)
  if r<abs(u)/(abs(u)+abs(v)):
    d=(u/(abs(u)),0)
  else:
    d=(0,v/(abs(v)))

  s=random.random()
  if(s<speed):
    return d
  else:
    return (0,0)

# if we cant move to vector sum of attrection and alignment then we just move closer to the flock as much as permitted
def adjacent_move_vec(x,y,a,b, boardsize):
  directions=[(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)]
  adjl=[]
  adje=[]
  stdd=dist(x,y,a,b, boardsize)
  for d in directions:
    (u,v)=d
    if dist(x+u,y+v,a,b, boardsize)<stdd:
      adjl.append(d)
  if dist(x+u,y+v,a,b, boardsize)==stdd:
      adje.append(d)

  if(adjl!=[]):
    return randomly(adjl)
  if(adje!=[]):
    return randomly(adje)

  return (0,0)

def initialise_birdpos(l,board):
  n=len(board)
  for b in l:
    b.x=random.randint(3,n-3)
    b.y=random.randint(3,n-3)
    while(board[b.x][b.y]!=None):
      b.x=random.randint(0,n-1)
      b.y=random.randint(0,n-1)
    board[b.x][b.y]=b
    b.history.append((b.x,b.y))

  return (l,board)

def centroid(lob):
  cx=0
  cy=0
  for b in lob:
    cx+=b.x
    cy+=b.y

  cx/=len(lob)
  cy/=len(lob)

  return(cx,cy)

#speed of attraction will be proportioanl to dist to centroid and inverse to size of cluster.
def set_speed(b,attributes):
  board=attributes['board']
  newb=copy.deepcopy(board)
  lofbirds=attributes['lob']
  attw=attributes['attw']
  aligw=attributes['aligw']
  thresh=attributes['threshold']
  mindist=attributes['mindist']
  maxdist=attributes['maxdist']
  time=attributes['time']
  boardsize=attributes['boardsize']

  similar_birds=findneighbours(b, attributes)
  if(similar_birds==[]):
    b.speed=round(random.random(),4)
    return b

  (cx,cy)=centroid(similar_birds)
  d2cntrd=dist(b.x,b.y,cx,cy, boardsize)

  if d2cntrd < 1.5:
    b.speed=0.5
  else:
    b.speed=round(0.5 + d2cntrd/boardsize,4)

  return b



def mean_dir(lob):
  dx=0
  dy=0
  for b in lob:
    dx+=b.dir[0]
    dy+=b.dir[1]

  dx/=len(lob)
  dy/=len(lob)
  return normalize(dx,dy)



def signed_vec(sc,tc, boardsize):  #sign of vector from sourcecord to target cord
  disp=abs(sc-tc)
  if disp==min(disp,boardsize-disp):
    sign2=1
  else:
    sign2=-1

  if(disp==0):
    sign=1 
  else:
    sign=tc-sc/disp
  return sign2*sign*disp

def attvec(bx,by,cx,cy, boardsize):
  svx=signed_vec(bx,cx, boardsize)
  svy=signed_vec(by,cy, boardsize)
  return normalize(svx,svy)

# weighted vector sum of alignment vector and attraction vector
def set_dir(b,attributes):
  board=attributes['board']
  newb=copy.deepcopy(board)
  lofbirds=attributes['lob']
  attw=attributes['attw']
  aligw=attributes['aligw']
  thresh=attributes['threshold']
  mindist=attributes['mindist']
  maxdist=attributes['maxdist']
  time=attributes['time']
  boardsize=attributes['boardsize']
  oriw=attributes['oriw']

  r=random.random()
  if r<0.1:
    b.dir=normalize(2*random.random()-1,2*random.random()-1)
    return b

  (ox,oy)=b.dir

  similar_birds=findneighbours(b, attributes)
  directions=[(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)]
  if(similar_birds==[]):
    b.speed=round(random.random(),4)

    return b

  (alx,aly)=mean_dir(similar_birds)
  (cx,cy)=centroid(similar_birds)
  #print(cx,"   ",cy)
  (atx,aty)=attvec(b.x,b.y,cx,cy, boardsize)

  dx=attw*atx+aligw*alx+oriw*ox
  dy=attw*aty+aligw*aly+oriw*oy
  b.dir=normalize(dx,dy)

  return b

def per_change(b1,time):
  b1t1=(float)(b1.list_val['close'][time])
  b1t0=(float)(b1.list_val['close'][time-1])
  b1pc=(b1t1-b1t0) / b1t0
  return b1pc

def mean_per_change(b1,time,tpsize):
  tnew=tpsize*(time+1)
  tprev=tpsize*(time)
  
  navg=0
  pavg=0
  for i in range(0,tpsize):
    navg+=(float)(b1.list_val['close'][tnew+i])
    pavg+=(float)(b1.list_val['close'][tprev+i])

  navg/=tpsize
  pavg/=tpsize

  pc=(navg-pavg)/pavg
  return pc

def floatify(l):
  newl=[]
  for i in l:
    newl.append((float)(i))
  return newl

def median_per_change(b1,time,tpsize):
  tnew=tpsize*(time+1)
  tprev=tpsize*(time)
  
  navg=(statistics.median(floatify(b1.list_val['close'][tnew:tnew+tpsize])))
  pavg=(statistics.median(floatify(b1.list_val['close'][tprev:tprev+tpsize])))

  pc=(navg-pavg)/pavg
  return pc

def samebr(a,b,l,u):
  if(a<=u and b<=u and a>=l and b>=l):
    return 1
  return 0

def similar_val1(b1,b2,time,t,tpsize,tpmode): #2 objects and time starting at 1
  #normalise similarity between 0 and 1, 1 being equal
  time=time+1
  if(b1.list_val['close'][time-1]==0 or b2.list_val['close'][time-1]==0):
    print("Error in data: Stock price can never be 0")
    return 0

  if tpmode=='mean':
    b1pc=mean_per_change(b1,time,tpsize)
    b2pc=mean_per_change(b2,time,tpsize)
  if tpmode=='median':
    b1pc=median_per_change(b1,time,tpsize)
    b2pc=median_per_change(b2,time,tpsize) 

  for i in [0,0.0001,0.001,0.01,0.1,1]:
    if samebr(b1pc,b2pc,i/10,i) or samebr(b1pc,b2pc,-i,-i/10):
      return 1

  if(b1pc==0):
    if abs(b2pc)<0.0001:
      return 1
  

  return 0

def similar_val2(b1,b2,time,t,tpsize,tpmode): #2 objects and time starting at 1
  #normalise similarity between 0 and 1, 1 being equal
  
  return 1

def similar_val3(b1,b2,time,t,tpsize,tpmode): 
  time=time+1
  if(b1.list_val['close'][time-1]==0 or b2.list_val['close'][time-1]==0):
    print("Error in data: Stock price can never be 0")
    return 0

  if tpmode=='mean':
    b1pc=mean_per_change(b1,time,tpsize)
    b2pc=mean_per_change(b2,time,tpsize)
  if tpmode=='median':
    b1pc=median_per_change(b1,time,tpsize)
    b2pc=median_per_change(b2,time,tpsize) 

  if samebr(b1pc,b2pc,t*b1pc,(2-t)*b1pc) or samebr(b1pc,b2pc,(2-t)*b1pc,t*b1pc):
    return 1

  if(b1pc==0):
    if abs(b2pc)<0.0001:
      return 1
  
  return 0

def similar_val4(b1,b2,time,t,tpsize,tpmode): 
  time=time+1
  if(b1.list_val['close'][time-1]==0 or b2.list_val['close'][time-1]==0):
    print("Error in data: Stock price can never be 0")
    return 0

  if tpmode=='mean':
    b1pc=mean_per_change(b1,time,tpsize)
    b2pc=mean_per_change(b2,time,tpsize)
  if tpmode=='median':
    b1pc=median_per_change(b1,time,tpsize)
    b2pc=median_per_change(b2,time,tpsize) 

  if b1pc==0:
    t=0
  else:
    bexp=abs((int)(math.log(abs(b1pc))))
    bexp=max(1.2,bexp*bexp)
    t=1/bexp

  if samebr(b1pc,b2pc,t*(b1pc+0.00001),(2-t)*(b1pc+0.00001)) or samebr(b1pc,b2pc,(2-t)*(b1pc+0.00001),t*(b1pc+0.00001)) :
    return 1

  if(b1pc==0):
    if abs(b2pc)<0.0001:
      return 1
  
  return 0

def similar_val(b1,b2,time,attributes):
  t=attributes['threshold']
  typen=attributes['simtype']
  tpsize=attributes['tpsize']
  tpmode=attributes['tpmode']
  if typen==1:
    return similar_val1(b1,b2,time,t,tpsize,tpmode)
  if typen==2:
    return similar_val2(b1,b2,time,t,tpsize,tpmode)
  if typen==3:
    return similar_val3(b1,b2,time,t,tpsize,tpmode)
  if typen==4:
    return similar_val4(b1,b2,time,t,tpsize,tpmode)

def findneighbours(b,attributes): # objec b and sample space l is a list of objects, t is threshold of being same species mindist os personal space marker, maxdist is distance of consideration
  simtype=attributes['simtype']
  board=attributes['board']
  newb=copy.deepcopy(board)
  attw=attributes['attw']
  aligw=attributes['aligw']
  t=attributes['threshold']
  mindist=attributes['mindist']
  maxdist=attributes['maxdist']
  time=attributes['time']
  boardsize=attributes['boardsize']
  l=attributes['lob']
  '''
  min_no=2
  most_similar=None
  if(l[0].x!=b.x or l[0].y!=b.y):
    most_similar=copy.deepcopy(l[0])
  else:
    most_similar=copy.deepcopy(l[1])
  scores=[]
  '''

  similar=[]
  for i in l:
    if(bdist(i,b, boardsize)<=maxdist and bdist(i,b, boardsize)>= mindist and similar_val(b,i, time,attributes)==1):
      btemp=copy.deepcopy(i)
      similar.append(btemp)

  return similar

def find_in_personal_space(b,l,mindist, maxdist,time, boardsize):
  inper=[]
  for i in l:
    if(dist(i,b, boardsize)<mindist and similar_val(i,b, time)>=t):
      btemp=copy.deepcopy(l[i])
      inper.append(btemp)

  return inper



def one_move(attributes):
  board=attributes['board']
  newb=copy.deepcopy(board)
  lofbirds=attributes['lob']
  attw=attributes['attw']
  aligw=attributes['aligw']
  thresh=attributes['threshold']
  mindist=attributes['mindist']
  maxdist=attributes['maxdist']
  time=attributes['time']
  boardsize=attributes['boardsize']
  
  def move(b,boardsize):
    (p,q)=move_vector(b.x,b.y,b.dir,b.speed)
    if p==0 and q==0:
      (p,q)=move_vector(b.x,b.y,b.dir,b.speed)
    else:
      u=b.x+b.dir[0] 
      u= u%boardsize
      v=b.y+b.dir[1]
      v=v%boardsize
      (p,q)=adjacent_move_vec(b.x,b.y,u,v,boardsize)
    return (p,q)
  
  newlob=[]
  for b in lofbirds:
    #print(b.name,"  ",b.dir, "  ",b.speed, end=" : ")
    b=set_dir(b,attributes)
    b=set_speed(b,attributes)
    #print(b.dir, "  ",b.speed)
    (p,q)=move(b,boardsize)
    px=(int)(b.x+p)% boardsize                #special (int)
    py=(int)(b.y+q)% boardsize

    if(board[px][py]!=None or newb[px][py]!=None ):
      (p,q)=move(b,boardsize)

    px=(int)(b.x+p)% boardsize
    py=(int)(b.y+q)% boardsize
    
    if(board[px][py]==None and newb[px][py]==None):
      board[b.x][b.y]=None
      newb[px][py]=b
      b.x=px
      b.y=py
      b.history.append((px,py))
    newlob.append(b)

    for bn in findneighbours(b,attributes):
      b.nbr[bn.name]+=1
      

  for b in newlob:
    attributes['board'][b.x][b.y]=b
  attributes['time']+=1
  attributes['lob']=newlob
  return attributes

def readBirds():
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
      
  #print("******************")
  return bdict

def init_game(n, bs):
  attributes={
      'attw':0.5,    #attraction vector weight
      'aligw':0.5,  #alignment vector weight
      'oriw': 0.2,  #momentum vector weight
      'mindist':1,   # separation :min distance between birds
      'maxdist':bs,  #maximum distance in sight of bird
      'threshold':0.5,    # threshold for similarity, between 0 and 1
      'time':1,
      'time limit':n,
      'lob':[],   # list of birds'
      
      'board':[],
      'boardsize':bs,
      'directions':[(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)],
      'simtype':3,
      'tpsize': 5,
      'tpmode':'mean' #mean or median

  } 


 
  directions=attributes['directions']
  
  boardsize=attributes['boardsize']
 
  for j in range(0,boardsize):
    temp=[]
    for i in range(0,boardsize):
      temp.append(None)
    attributes['board'].append(temp)

  #intialise birds and values   
  #read dict bdict name: [close values between 2013-2017]
  bdict=readBirds()

  nbrdict={}
  
  for bname in bdict:
    attributes['lob'].append(Bird(bname,bdict[bname],boardsize))
    nbrdict[bname]=0


  (attributes['lob'],attributes['board'])=initialise_birdpos(attributes['lob'],attributes['board'])
  
  for b in attributes['lob']:
    b.nbr=copy.deepcopy(nbrdict)

  return attributes

def nbrnames(b,time, attributes,boardsize):
  nbr=findneighbours(b, attributes)
  names=[]
  for i in nbr:
    names.append(i.name)
  return names

def simulate(n):
  boardsize=25
  attributes=init_game(n, boardsize)
  l=attributes['lob']
  attributes['lob']=l
  #for b in attributes['lob']:
  #  print(b.name,"       ",len(b.list_val['close']))
  #printsimilarity(time,attributes)
  print("Intialising Swarms...")
  print(" ")

  for i in range(0,n):
    attributes=one_move(attributes)
    print("")
    print("")
    print("   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *")
    print("")
    print("")
    print("")
    print("")
    print("")
    print("")
    print("")
    print("")
    print("")

    printboard(boardsize,attributes)

  for b in l:
    print(b.name,end="   ")

    for i in b.nbr:
      if b.nbr[i]>min(n/7,7):
        print(i,"  ",b.nbr[i],end=" ")
    print(" ")
  #printhistory(l,boardsize)

  #printnbrs(attributes,l,boardsize,n)

def printsimilarity(time,attributes):
  l=attributes['lob']
  simtype=attributes['simtype']
  t=attrinutes['threshold']

  for b1 in l:
    for b2 in l:
      print(b1.name," , ",b2.name," :  ",similar_val(b1,b2,time,t,simtype))


def printnbrs(attributes,l,boardsize,n):
  for i in range(0,n):
    print(i)
    for b in l:
      print(b.name,"  : ",nbrnames(b,i,attributes,boardsize))


def printperchange(attributes):
  for b in attributes['lob']:
    print(b.name)#,"       ",b.list_val['close'])

    for i in range(0,n):
      print("       ",per_change(b,i))
    print("****")
    print(" ")
  


def printhistory(l,boardsize):
  for b in l:
    for i in range(0,boardsize):
      for j in range(0,boardsize):
        if (i,j) in b.history:
          print("*",end=" ")
        else:
          print(" ",end=" ")
      print("")


def printboard(boardsize,attributes):
  for i in range(0,boardsize):
    for j in range(0,boardsize):
      bo=attributes['board']
      if(bo[i][j]==None):
        print(" ",end=" ")
      else:
        name=(bo[i][j].name)
        if len(name)<1:
          print("I",end=" ")
        else:
          print(name[0],end=" ")
    print("")
  print("******************")


simulate(500)


