import copy
from Fetch import fetch
from Decode import decode
from Execute import execute
from MemoryAcess import memory_access
from WriteBack import write_back
from include import *

def run_main():

    if(knob.knob1==0): #Work in normal single cycle manner
        Clock = 1
        while True:
            isDone = fetch()
            if(isDone):
                break
            decode()
            execute()
            memory_access()
            write_back()
            print("Clock Cycle No.", Clock)
            print()
            Clock += 1
    
    else: 
        #Pipelined Execution
        #Each stage will take two arguments-> That are two pipeline register, one from which it will read and one to which it will write at the end of the cycle.
        Clock=1
        while True:
            if(pReg.MA_WB.get('inst_encoding')!=None and pReg.MA_WB['inst_encoding']==TerminationCode and pReg.EX_MA['inst_encoding']==TerminationCode and pReg.DE_EX['inst_encoding']==TerminationCode and pReg.IF_DE['inst_encoding']==TerminationCode):
                print("WRITEBACK: Terminated")
                print("ALL INSTRUCTIONS EXECUTED SUCCESSFULLY")
                print()
                with open("register_values.mc", "w+") as f:
                    for i in range(0, len(mem.RegisterFile)):
                        f.write("X{}:  {}\n".format(i, mem.RegisterFile[i]))
                with open("data_mem.mc", "w+") as p: 
                    for i in mem.data_memory:
                        p.write("{}:  {}\n".format(hex(i), mem.data_memory[i]))
                stat.DataStalls+=(stat.TotalStalls-stat.DataStalls-stat.ControlStalls)
                break
            print("Pipelined Clock Cycle No.", Clock)
            if(pReg.MA_WB != {}):
                write_back(pReg.MA_WB)
            if(pReg.EX_MA != {}):
                memory_access(pReg.EX_MA, pReg.MA_WB)
            if(pReg.DE_EX != {}):
                execute(pReg.DE_EX, pReg.EX_MA)
            if(pReg.IF_DE != {}):
                decode(pReg.IF_DE, pReg.DE_EX)
            fetch(pReg.IF_DE) #This stage will only write to the IF_DE pipeline register after fetching the instruction.

            if(knob.knob3==1):
                print()
                print("Values in Register File at the end of Cycle",Clock)
                for i in range(0,len(mem.RegisterFile)):
                    print("X"+str(i)+"="+str(mem.RegisterFile[i]),end=" ")
                print()
            
            if(knob.knob4==1):
                print()
                print("Information in Pipeline Registers at the end of Cycle",Clock)
                print("IF_DE =",pReg.IF_DE)
                print("DE_EX =",pReg.DE_EX)
                print("EX_MA =",pReg.EX_MA)
                print("MA_WB =",pReg.MA_WB)

            if(knob.knob5==1):
                #Taking a snapshot of the pipeline registers for the specified instruction No.
                if(pReg.IF_DE!={} and (pReg.IF_DE.get('PC')//4 +1)==knob.instrNoInp):
                    knob.if_de=copy.deepcopy(pReg.IF_DE)
                if(pReg.DE_EX!={} and (pReg.DE_EX.get('PC')//4 +1)==knob.instrNoInp):
                    knob.de_ex=copy.deepcopy(pReg.DE_EX)
                if(pReg.EX_MA!={} and (pReg.EX_MA.get('PC')//4 +1)==knob.instrNoInp):
                    knob.ex_ma=copy.deepcopy(pReg.EX_MA)
                if(pReg.MA_WB!={} and (pReg.MA_WB.get('PC')//4 +1)==knob.instrNoInp):
                    knob.ma_wb=copy.deepcopy(pReg.MA_WB)

            Clock+=1
            print()
        
        if(knob.knob5==1):
            print("Information in Pipeline Registers for Instruction No.",knob.instrNoInp)
            print("IF_DE=",knob.if_de)
            print()
            print("DE_EX=",knob.de_ex)
            print()
            print("EX_MA=",knob.ex_ma)
            print()
            print("MA_WB=",knob.ma_wb)
            print()

        stat.TotalCycles = Clock-1
        stat.CPI = round(stat.TotalCycles/stat.TotalinstEX,4)
        stat.TotalControlHazards = lock.ControlH
        stat.TotalDataHazards = lock.DataH
        stat.TotalBranchMispred = Branch.Mispred
        print()

        stat.writeStats()