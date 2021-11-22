import dataclasses
import math

'''
    dataclass representing a worklogged issue
'''
@dataclasses.dataclass
class IssueInfo:
    code : str
    comment : str
    startHr : int
    startMin : int
    duration : float

    def setDur(self, hrs: int, mins: int) -> None:
        mins = roundTo15(mins)

        self.duration = float(hrs)
        self.duration = self.duration + (mins/60) 

        #print("DURATION: ", self.duration)
    
    def getDur(self) -> list[int]:
        hrsComponent : int = int(math.floor(self.duration))
        minsComponent : int = int((self.duration - hrsComponent) * 60)
        return [hrsComponent, minsComponent]

    def __str__(self) -> str:
        finishHr : int = int(self.startHr + math.floor(self.duration))
        finishMin : int = int(self.startMin + ((self.duration - math.floor(self.duration)) * 60))

        if finishMin > 59:
            finishMin = finishMin - 60
            finishHr = finishHr + 1

        return f'{self.startHr}:{self.startMin} -> {finishHr}:{finishMin} ({self.duration}hrs)    [{self.code}]: {self.comment}'
    
'''
    rounds to nearest 15
'''
def roundTo15(value : int) -> int:
    base = 15
    #print ("IN: ",value)
    #print ("OUT: ",round(value/base))
    return base * round(value/base)