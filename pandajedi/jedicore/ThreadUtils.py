import sys
import time
import threading
import multiprocessing


# list with lock
class ListWithLock:
    def __init__(self,dataList):
        self.lock = threading.Lock()
        self.dataList  = dataList
        self.dataIndex = 0

    def __contains__(self,item):
        self.lock.acquire()
        ret = self.dataList.__contains__(item)
        self.lock.release()
        return ret

    def append(self,item):
        self.lock.acquire()
        appended = False
        if not item in self.dataList:
            self.dataList.append(item)
            appended = True
        self.lock.release()
        return appended

    def get(self,num):
        self.lock.acquire()
        retList = self.dataList[self.dataIndex:self.dataIndex+num]
        self.dataIndex += len(retList)
        self.lock.release()
        return retList

    def stat(self):
        self.lock.acquire()
        total = len(self.dataList)
        nIndx = self.dataIndex
        self.lock.release()
        return total,nIndx



# map with lock
class MapWithLock:
    def __init__(self,dataMap=None):
        self.lock = threading.Lock()
        if dataMap == None:
            dataMap = {}
        self.dataMap  = dataMap

    def __getitem__(self,item):
        ret = self.dataMap.__getitem__(item)
        return ret

    def __setitem__(self,item,value):
        self.dataMap.__setitem__(item,value)

    def __contains__(self,item):
        ret = self.dataMap.__contains__(item)
        return ret

    def acquire(self):
        self.lock.acquire()

    def release(self):
        self.lock.release()

    def add(self,item,value):
        if not item in self.dataMap:
            self.dataMap[item] = 0
        self.dataMap[item] += value

    def get(self,item):
        if not item in self.dataMap:
            return 0
        return self.dataMap[item]



# thread pool
class ThreadPool:
    def __init__(self):
        self.lock = threading.Lock()
        self.list = []

    # add thread
    def add(self,obj):
        self.lock.acquire()
        self.list.append(obj)
        self.lock.release()
        
    # remove thread
    def remove(self,obj):
        self.lock.acquire()
        try:
            self.list.remove(obj)
        except:
            pass
        self.lock.release()
        
    # join
    def join(self,timeOut=None):
        thrlist = tuple(self.list)
        for thr in thrlist:
            try:
                thr.join(timeOut)
                if thr.isAlive():
                    break
            except:
                pass

    # remove inactive threads
    def clean(self):
        thrlist = tuple(self.list)
        for thr in thrlist:
            if not thr.isAlive():
                self.remove(thr)
        
    # dump contents
    def dump(self):
        thrlist = tuple(self.list)
        nActv = 0
        nDone = 0
        for thr in thrlist:
            if thr.isAlive():
                nActv += 1
        return 'nActive={0}'.format(nActv)



# thread class working with semaphore and thread pool
class WorkerThread (threading.Thread):

    # constructor
    def __init__(self,workerSemaphore,threadPool,logger):
        threading.Thread.__init__(self)
        self.workerSemaphore = workerSemaphore
        self.threadPool = threadPool
        self.threadPool.add(self)
        self.logger = logger

    # main loop
    def run(self):
        # get slot
        if self.workerSemaphore != None:
            self.workerSemaphore.acquire()
        # execute real work
        try:
            self.runImpl()
        except:
            errtype,errvalue = sys.exc_info()[:2]
            self.logger.error("%s crashed in WorkerThread.run() with %s:%s" % \
                              (self.__class__.__name__,errtype.__name__,errvalue))
        # remove self from thread pool
        self.threadPool.remove(self)
        # release slot
        if self.workerSemaphore != None:
            self.workerSemaphore.release()
            


# thread class to cleanup zombi processes
class ZombiCleaner (threading.Thread):

    # constructor
    def __init__(self,interval=20):
        threading.Thread.__init__(self)
        self.interval = interval


    # main loop
    def run(self):
        while True:
            x = multiprocessing.active_children()
            time.sleep(self.interval)
