import pandas as pd
class Machine(object):
    def __init__(self):
        self.state = []
        self.event = []
        self.transition = 0

    def getStatesOrEvents(self, source, line, tag):
        line = source.readline()
        while line:
            if line.__contains__("}"):
                return
            str_line = line.strip()
            str_line = str_line.replace(',','')
            if tag == 1:
                self.state.append(str_line)
            else:
                self.event.append(str_line)
            line = source.readline()
    
    def getTransition(self):
        col = {}
        for each in self.event:
            col[each] = [0 for x in range(0, len(self.state))]
        self.transition = pd.DataFrame(col, index=self.state)
    
    def getStateFromFunction(self, line):
        str_line = line.strip()
        tokens = str_line.split(" ")
        index = tokens[1].index(":")
        return tokens[1][0:index]
    
    def getTransiteState(self, line):
        str_line = line.strip()
        tokens = str_line.split(" ")
        index = tokens[2].index(";")
        return tokens[2][0:index]

    def getTransitionTable(self, source, line):
        while line and not line.__contains__("end;"):
            line = source.readline()
            if line.__contains__("switch") and (line.__contains__("state") or line.__contains__("State")):
                while line:
                    if line.__contains__("case"): ##for each state
                        temp_state = self.getStateFromFunction(line)
                        line = source.readline()
                        trigger_event = {}
                        # actions = []
                        while line and not line.__contains__("endswitch"):
                            if line.__contains__("case"):
                                key = self.getStateFromFunction(line)
                                while line and not line.__contains__("/n"):
                                    if line.__contains__("state") or line.__contains__("State"):
                                        value = self.getTransiteState(line)
                                    line = source.readline()
                                trigger_event[key] = value
                            line = source.readline()
                    line = source.readline()
    