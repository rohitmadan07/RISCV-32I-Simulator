from include import *

def memory_access(EX_MA={},MA_WB={}):
  #EX_MA -> pipeline register from which we read
  #MA_WB -> pipeline register to which we write

  if(knob.knob2==1 and lock.LoadUseMAStall==True):
    lock.LoadUseMAStall=False
    lock.LoadUseWBStall=True
    stat.TotalStalls = stat.TotalStalls+1
    stat.DataStalls+=1
    print("MEMORY: No Operation (Bubble) Because of Load Use Data Hazard")
    return

  if(knob.knob1==1 and EX_MA['inst_encoding']==TerminationCode):
    MA_WB['inst_encoding'] = EX_MA['inst_encoding']
    lock.StallMA=False
    print("MEMORY: Terminated")
    return
  
  if(lock.StallEX==True):
    if(lock.controlHazard==True): stat.ControlStalls+=1
    else: stat.DataStalls+=1
    lock.StallMA=True
    stat.TotalStalls = stat.TotalStalls+1
    print("MEMORY: No Operation (bubble)")
    return
  
  if(lock.StallMA==True):
    stat.TotalStalls = stat.TotalStalls+1
    if(lock.controlHazard==True): stat.ControlStalls+=1
    else: stat.DataStalls+=1
    print("MEMORY: No Operation (Bubble)")
    return
  
  if(knob.knob1==1): #For pipeline
    #lock.StallMA=False
    lock.StallWB=False
    #Loading data from the pipeline registers
    pkt.ALUResult = EX_MA['ALUResult']
    pkt.op2 = EX_MA['op2']
    pkt.inst = EX_MA['inst']
    control.MemOP = EX_MA['control']['MemOP']

    if(knob.knob2==1):#Forwarding (Overwriting)
      #print(frwd.forwardDataWrite)
      if(frwd.forwardDataWrite==2 and control.MemOP==1): #Use forwarded value only when Writing to data memory
        if(MA_WB['opcode']=='0000011'):pkt.op2 = MA_WB['LoadData'] #Store After Load Case
        else: pkt.op2 = MA_WB['ALUResult'] #Store After Dependency Case
        frwd.ResetMA()
      #print(pkt.op2)

  if control.MemOP == 0: #Write Disabled
    if pkt.ALUResult in mem.data_memory:
      pkt.LoadData = mem.data_memory[pkt.ALUResult]
    else:
      pkt.LoadData = 0
    
    if(pkt.inst=="lb"):
      pkt.LoadData = pkt.LoadData&0xFF  # Considering only first(LSB) 8 bits of LoadData as rd = M[rs1+imm][0:7] #Byte=8bits
      print("MEMORY: ", pkt.LoadData , "Loaded from address " + hex(pkt.ALUResult))
      stat.TotalDataStoreinst = stat.TotalDataStoreinst+1

    elif(pkt.inst=="lh"):
      pkt.LoadData = pkt.LoadData&0xFFFF # Considering only first(LSB) 16 bits of LoadData as rd = M[rs1+imm][0:15] #Half-word = 16bits/2bytes
      print("MEMORY: ", pkt.LoadData , "Loaded from address " + hex(pkt.ALUResult))
      stat.TotalDataStoreinst = stat.TotalDataStoreinst+1

    elif(pkt.inst=="lw"):
      pkt.LoadData = pkt.LoadData&0xFFFFFFFF # Considering all 32 bits of LoadData as rd = M[rs1+imm][0:31] #Word = 32bits/4bytes
      print("MEMORY: ", pkt.LoadData , "Loaded from address " + hex(pkt.ALUResult))
      stat.TotalDataStoreinst = stat.TotalDataStoreinst+1

  else:
    dataStore = 0
    if(pkt.inst=="sb"):
      dataStore = (pkt.op2&0x000000FF)
      #Storing first 8 (LSB) bits of rs2 in first 8 (LSB) bits of Data memory #Byte=8bits
      mem.data_memory[pkt.ALUResult]= (mem.data_memory[pkt.ALUResult]&0xFFFFFF00)|(pkt.op2&0x000000FF) 
      print("MEMORY: " + "Storing" , dataStore , "at address" , hex(pkt.ALUResult))
      stat.TotalDataStoreinst = stat.TotalDataStoreinst+1

    elif(pkt.inst=="sh"):
      dataStore = (pkt.op2&0x0000FFFF)
      #Storing first 16 (LSB) bits of rs2 in first 16 (LSBs) bits of Data memory #Half-word = 16bits/2bytes
      mem.data_memory[pkt.ALUResult]=(mem.data_memory[pkt.ALUResult]&0xFFFF0000)|(pkt.op2&0x0000FFFF)
      print("MEMORY: " + "Storing" , dataStore , "at address" , hex(pkt.ALUResult))
      stat.TotalDataStoreinst = stat.TotalDataStoreinst+1

    elif(pkt.inst=="sw"):
      dataStore = pkt.op2
      #Storing all bits of rs2 in all bits of Data memory #Word = 32bits/4bytes
      mem.data_memory[pkt.ALUResult]=dataStore
      print("MEMORY: " + "Storing" , dataStore , "at address" , hex(pkt.ALUResult))
      stat.TotalDataStoreinst = stat.TotalDataStoreinst+1

    
    if pkt.ALUResult in mem.data_memory:
      pkt.LoadData = mem.data_memory[pkt.ALUResult]
    else:
      pkt.LoadData = 0
      
  if(knob.knob1==1):
      MA_WB['PC'] = EX_MA['PC']
      MA_WB['LoadData'] = pkt.LoadData
      MA_WB['ALUResult'] = pkt.ALUResult
      MA_WB['inst'] = pkt.inst
      MA_WB['control'] = EX_MA['control']
      MA_WB['ImmU']=EX_MA['ImmU']
      MA_WB['ImmI']=EX_MA['ImmI']
      MA_WB['ImmS']=EX_MA['ImmS']
      MA_WB['rd'] = EX_MA['rd']
      MA_WB['rs1'] = EX_MA['rs1']
      MA_WB['rs2'] = EX_MA['rs2']
      MA_WB['inst_encoding'] = EX_MA['inst_encoding'] 
      MA_WB['inst_format'] = EX_MA['inst_format'] 
      MA_WB['opcode'] = EX_MA['opcode']


  if(pkt.inst not in ["lb","lh","lw","sb","sh","sw"]):
    if(knob.knob1==1):
      print("MEMORY: No Memory Operation => Instruction No. " + str(((EX_MA['PC']//4) + 1)))
    else:
      print("MEMORY: No Memory Operation")