class Forwarding:
    #EX STAGE
    
    '''3 Options
        1. DE_EX['OP1'] -> from previous cycle (from register file)
        2. Forward from MA stage (written by previous EX) using EX_MA register (Using previous cycle ALU Result) (Consecutive instr. Data hazard case)
        3. Forward from WB stage (written by previous MA) using MA_WB register (1.Load With gap of 1 2.Load Use Data Hazard 2.Gap of 1 data hazard (ALUResult forwarded from MA_WB in WB) 3.LUI instruction, Forward ImmU)
        Forwarding always done at starting of stage as the previous stage would have written to the pipeline register of it and next stage
        which we can acess in start of next stage.
    '''
    forwardInp1=1 #OP1 MUX
    forwardInp2=1 #OP2 MUX

    def ResetEX(self):
        self.forwardInp1=1
        self.forwardInp2=1

    #MA Stage
    ''' 2 Options for DataWrite to Data Memory
        1. EX_MA['OP2] -> from previous cycle
        2. MA_WB['LoadData] -> Forwarded from MA_WB of WB stage to MA

        Store After Load Case
    '''
    #MUX for DataWrite
    forwardDataWrite=1
    def ResetMA(self):
        self.forwardDataWrite=1
