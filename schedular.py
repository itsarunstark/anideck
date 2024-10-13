import threading
from typing import Callable, Dict, List, Tuple
from enum import Flag
import time

class Priority(Flag):
    PRIORITY_HIGH = 0xff
    PRIORITY_LOW = 0x0f
    PRIORITY_MID = 0xf0


class Job:
    def __init__(self, jobFunction:Callable, *jobArgs):
        self.jobFunction = jobFunction
        self.orphanJob = True
        self.jobArgs = jobArgs
        self.jobPID = 0
        self.running = False
        self.callback_function = lambda x:None
        self.result = None
        self.completed = False
        # self.jobs = 0
    
    def execute(self):
        if (self.orphanJob) :
            print("Orphan jobs can't be executed")
            return self.result
        self.running = True
        self.result = self.jobFunction(*self.jobArgs)
        self.running = False
        return self.result

class SchedularState(Flag):
    STATE_IDLE = 0x01
    STATE_NON_IDLE = 0x02
    STATE_STOPPED = 0x04
    STATE_RUNNING = 0x08
    STATE_PAUSED = 0x10

class Schedular:
    def __init__(self):
        self.workQueue:Dict[Priority, List[Job]] = {
            Priority.PRIORITY_HIGH:[],
            Priority.PRIORITY_MID:[],
            Priority.PRIORITY_LOW:[]
        }
        self.state = SchedularState.STATE_STOPPED
        self.thread = None
        self.break_time = 0.016
        self.jobs = 0

    def start(self):
        if (self.state & SchedularState.STATE_RUNNING):
            print("Schedular is already running")
            return True
        if (self.state & SchedularState.STATE_STOPPED):
            self.state = SchedularState.STATE_RUNNING | SchedularState.STATE_IDLE
            self.thread = threading.Thread(
                target=self._scheduleloop,daemon=True
            )
            self.thread.start()
            return True
    
    def _scheduleloop(self):
        while(self.state & SchedularState.STATE_RUNNING):
            time.sleep(self.break_time)
            while self.workQueue[Priority.PRIORITY_HIGH]:
                self.state = (self.state)&(~SchedularState.STATE_IDLE)
                job = self.workQueue[Priority.PRIORITY_HIGH].pop(0)
                job.execute()
                job.callback_function(job)
                job.completed = True
                self.jobs -= 1
            
            while self.workQueue[Priority.PRIORITY_MID]:
                self.state = (self.state)&(~SchedularState.STATE_IDLE)
                job = self.workQueue[Priority.PRIORITY_MID].pop(0)
                job.execute()
                job.callback_function(job)
                job.completed = True
                self.jobs -= 1
            
            while self.workQueue[Priority.PRIORITY_LOW]:
                self.state = (self.state)&(~SchedularState.STATE_IDLE)
                job = self.workQueue[Priority.PRIORITY_LOW].pop(0)
                job.execute()
                job.callback_function(job)
                job.completed = True
                self.jobs -= 1
            self.state |= SchedularState.STATE_IDLE
        self.state &= ~SchedularState.STATE_RUNNING
    
    def stop(self):
        self.state &= ~SchedularState.STATE_RUNNING
    
    def queueJob(self, job:Job, priority:Priority=Priority.PRIORITY_MID):
        job.orphanJob = False
        job.completed = False
        job.running = False
        self.workQueue[priority].append(job)
        self.jobs += 1

def printHello(x):
    print("Hello, {}!".format(x))

if __name__ == '__main__':
    sch = Schedular()
    print(sch.state)
    sch.start()
    print(sch.state)
    job = Job(printHello, "Arun Kumar")
    sch.queueJob(job)
    while (sch.jobs):
        print(sch.state)
        time.sleep(0.1)
    print(job.result)
    # sch.stop()
    
