class Stats:
    TotalCycles = 0
    TotalinstEX = 0
    CPI = 0
    TotalDataStoreinst = 0
    TotalALUinst = 0
    TotalControlInst = 0
    TotalStalls = 0
    TotalDataHazards = 0
    TotalControlHazards = 0
    TotalBranchMispred = 0
    DataStalls = 0
    ControlStalls = 0

    def writeStats(self):
        with open("OutputStats.txt","w+") as f:
            f.write("Total number of cycles: {}\n".format(self.TotalCycles))
            f.write("Total instructions executed: {}\n".format(self.TotalinstEX))
            f.write("Cycles per Instruction (CPI): {}\n".format(self.CPI))
            f.write("Number of Data-transfer (load and store) instructions executed: {}\n".format(self.TotalDataStoreinst))
            f.write("Number of ALU instructions executed: {}\n".format(self.TotalALUinst)) 
            f.write("Number of Control instructions executed: {}\n".format(self.TotalControlInst))
            f.write("Number of stalls/bubbles in the pipeline: {}\n".format(self.TotalStalls))
            f.write("Number of data hazards: {}\n".format(self.TotalDataHazards))
            f.write("Number of control hazards: {}\n".format(self.TotalControlHazards))
            f.write("Number of branch mispredictions: {}\n".format(self.TotalBranchMispred))
            f.write("Number of stalls due to data hazards: {}\n".format(self.DataStalls))
            f.write("Number of stalls due to control hazards: {}\n".format(self.ControlStalls))
    
