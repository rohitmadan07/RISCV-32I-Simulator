from include import *

def fetch(IF_DE={}):
    #IF_DE-> Pipeline register to which this stage writes information at the end of cycle.

    if(knob.knob2==1 and lock.LoadUseIFStall==True):
      lock.LoadUseIFStall=False
      stat.TotalStalls = stat.TotalStalls+1
      stat.DataStalls+=1
      print("FETCH: STALLED Because of Load Use Data Hazard")
      return
    
    if lock.StallIF==True:
      stat.TotalStalls = stat.TotalStalls+1
      stat.DataStalls+=1
      print("FETCH: NO OPERATION") #No operation
      if(lock.Branch == True): #control hazard in a data hazard
        if(control.isBranch==1):
          control.isBranch =0
          IF_DE['PC'] = pkt.BranchTarget
          pkt.PC=IF_DE['PC']
        lock.StallDE=True
        lock.BranchinDE=False
        stat.DataStalls-=1
        stat.ControlStalls+=1
      return
    
    else:
      inst_encoding = mem.instruction_memory.get(pkt.PC)
      if(knob.knob1==1 and inst_encoding == TerminationCode):
        if(lock.BranchNotTaken):
          stat.TotalStalls = stat.TotalStalls+1
          lock.BranchNotTaken=False
          #IF_DE['inst_encoding'] = inst_encoding
          lock.StallDE=True
          print("FETCH: NO OPERATION due to Branch instruction in Execute and Termination reached")
          lock.BranchinDE=False
          lock.BranchNotTaken=False
          stat.ControlStalls+=1
        
        elif(lock.Branch==True):
          stat.TotalStalls = stat.TotalStalls+1
          stat.ControlStalls+=1
          print("FETCH: NO OPERATION due to Branch instruction in Execute which will be taken and Termination Reached")
          if(control.isBranch==1):
            if(lock.Branch==True):
              control.isBranch =0
            IF_DE['PC'] = pkt.BranchTarget
            pkt.PC=IF_DE['PC']

        elif(lock.BranchinDE):
          lock.BranchinDE=False
          lock.BranchNotTaken=False
          stat.TotalStalls = stat.TotalStalls+1
          print("FETCH: NO OPERATION due to Branch instruction in Decode and Termination Reached")
          stat.ControlStalls+=1

        else:
          IF_DE['inst_encoding'] = inst_encoding 
          print("FETCH : TERMINATED")
          lock.BranchinDE=False
          lock.BranchNotTaken=False


        return
      
      elif(knob.knob1==0 and inst_encoding == TerminationCode):
        print("All instructions executed successfully")
        print(mem.data_memory)
        with open("register_values.mc", "w+") as f:
          for i in range(0, len(mem.RegisterFile)):
            f.write("X{}:  {}\n".format(i, mem.RegisterFile[i]))
        with open("data_mem.mc", "w+") as p: 
          for i in mem.data_memory:
            p.write("{}:  {}\n".format(hex(i), mem.data_memory[i]))
        return True
      
      lock.BranchinDE=False
      lock.BranchNotTaken=False
      currentPC = pkt.PC
      pkt.inst_hex = hex(inst_encoding) #hexadecimal string representation
      
      if(knob.knob1==1):
          
        #If a Branch instruction is fetched in current cycle then we want to use our branch predictor to predict the direction of the branch.
        #In the next cycle the branch would move to Decode stage where an entry corresponding to it would be made in the BTB
        #So we then fetch Branch Target from the BTB corresponding to that branch
        #In the next cycle when the branch reaches Execute stage then we get to know whether branch prediction was correct or not and whether we need to flush the pipeline
        if(pReg.DE_EX!={} and pReg.DE_EX['inst_format']=='B'):
          if(Branch.BTB[pReg.DE_EX['PC']][1]==1): 
            #Counter =1 -> Prediction is to take the branch
            nextPC = pkt.PC + Branch.BTB[pReg.DE_EX['PC']][0]
          else: 
            #Counter=0 -> Prediction is to not take the branch
            nextPC = pkt.PC +4
          
        if(control.isBranch==0): 
          pkt.PC = pkt.PC+4 
          IF_DE['PC'] = currentPC
        elif(control.isBranch==1):
          if(lock.Branch==True):
            control.isBranch =0
          IF_DE['PC'] = pkt.BranchTarget
          pkt.PC=IF_DE['PC']
        else : IF_DE['PC'] = pkt.ALUResult; pkt.PC=IF_DE['PC']
        IF_DE['inst_encoding'] = inst_encoding 
        IF_DE['inst_hex'] = pkt.inst_hex
      #For single cycle case..PC is updated in execute stage

      if(knob.knob1==1):
        print("FETCH : Fetch Instruction", pkt.inst_hex, "from address", hex(currentPC), "=> Instruction No."+str(((currentPC//4)+1)))
      else:
        print("FETCH : Fetch Instruction", pkt.inst_hex, "from address", hex(currentPC))
      