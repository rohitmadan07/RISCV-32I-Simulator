from SignedExtension import signedExtension,signed32
from include import *

def decode(IF_DE={}, DE_EX={}):
  #IF_DE -> pipeline register from which we read
  #DE_EX -> pipeline register to which we write

  if(knob.knob2==1 and lock.LoadUseDEStall==True):
    lock.LoadUseIFStall=True
    lock.LoadUseDEStall=False
    stat.TotalStalls = stat.TotalStalls+1
    stat.DataStalls+=1
    print("DECODE: STALLED Because of Load Use Data Hazard")
    return

  if(knob.knob1==1 and IF_DE['inst_encoding']==TerminationCode):
    DE_EX['inst_encoding'] = IF_DE['inst_encoding']
    lock.StallDE=False
    print("DECODE: TERMINATED")
    return

  
  if(lock.Writing==True):
    stat.TotalStalls = stat.TotalStalls+1
    stat.DataStalls+=1
    print("DECODE: STALLED at Instruction No.",str(((IF_DE['PC']//4) + 1)))
    lock.Writing=False
    lock.currChange =True
    return
  
  elif(lock.Writing==False and lock.currChange==True):
    lock.StallDE=False
    lock.StallIF=False

  if lock.StallDE == True :
    stat.TotalStalls = stat.TotalStalls+1
    if(lock.controlHazard==True):
      stat.ControlStalls+=1
      print("DECODE: NO OPERATION (BUBBLE)")
    else:
      stat.DataStalls+=1
      print("DECODE: STALLED")
    return
  
  else: 
    if(knob.knob1==1): pkt.inst_hex  = IF_DE['inst_hex']
    res = (bin(int(pkt.inst_hex, 16))[2:]).zfill(32) #binary representation of the instruction

    opcode = res[25:32]
    pkt.rd = int(res[20:25],2)
    funct3 = int(res[17:20],2)
    pkt.rs1 = int(res[12:17],2)
    pkt.rs2 = int(res[7:12],2)
    funct7 = int(res[0:7],2)
    pkt.op1 = mem.RegisterFile[pkt.rs1]
    pkt.op2 = mem.RegisterFile[pkt.rs2]

    pkt.ImmI = signed32(signedExtension(int(res[0:12],2)))
    pkt.ImmS = signed32(signedExtension(int(res[0:7]+res[20:25],2)))
    pkt.ImmB = signed32(signedExtension(int(res[0]+res[24]+res[1:7]+res[20:24]+str(0),2)))
    pkt.ImmJ = signed32(signedExtension(int(res[0]+res[12:20]+res[11]+res[1:11],2),True))
    pkt.ImmU = signed32(int(res[0:20],2)<<12) 

    if lock.LoadUseMAStall==False: # Skip Hazard Detection for one cycle after detecting a Load Use Hazard as anyways stalled
      if(knob.knob1==1 and lock.currChange == False):
        DE_EX['PC']=IF_DE['PC']
        DE_EX['rd'] = pkt.rd
        DE_EX['rs1'] = pkt.rs1
        DE_EX['rs2'] = pkt.rs2
        DE_EX['opcode'] = opcode
        lock.detectRAW(pReg.DE_EX,pReg.EX_MA,pReg.MA_WB,knob,frwd) #Hazard Detection

        if(lock.StallDE==True): #No Forwarding
          stat.DataStalls+=1
          print("DECODE: Stalled")
          return
      
    lock.currChange=False
    lock.StallEX=False

    if opcode=="0110011":
      pkt.inst_format = "R"
      control.controlRtype() #Sets the required control signals for this particular format
      if(funct3==0):
        if(funct7==0):
          pkt.inst="add"
        else:
          pkt.inst="sub"
      elif(funct3==1):
        pkt.inst="sll"
      elif(funct3==2):
        pkt.inst="slt"
      elif(funct3==4):
        pkt.inst="xor"
      elif(funct3==5):
        pkt.inst="srl"
      elif(funct3==6):
        pkt.inst="or"
      elif(funct3==7):
        pkt.inst="and"
      
      print("DECODE:","Instruction format:",pkt.inst_format,", Operation:",pkt.inst,", First Operand x"+str(pkt.rs1),", Second Operand x"+str(pkt.rs2),", Destination Register x"+str(pkt.rd))
      print("DECODE:","Read Registers:","x"+str(pkt.rs1)+"="+str(pkt.op1),", x"+str(pkt.rs2)+"="+str(pkt.op2))

    elif opcode=="0010011":
      pkt.inst_format = "I"
      control.controlItype() #Control
      if(funct3==0):
        pkt.inst="addi"
      elif(funct3==6):
        pkt.inst="ori"
      elif(funct3==7):
        pkt.inst="andi"

      print("DECODE:","Instruction format:",pkt.inst_format,", Operation:",pkt.inst,", First Operand x"+str(pkt.rs1),", Immediate value ",pkt.ImmI,", Destination Register x"+str(pkt.rd))
      print("DECODE:","Read Registers:","x"+str(pkt.rs1)+"="+str(pkt.op1))
      
    elif opcode=="0000011":
      pkt.inst_format = "I"
      control.controlLoad() #Control
      if(funct3==0):
        pkt.inst="lb"
      elif(funct3==1):
        pkt.inst="lh"
      elif(funct3==2):
        pkt.inst="lw"
      elif(funct3==4):
        pkt.inst="lbu"
      elif(funct3==5):
        pkt.inst="lhu"

      print("DECODE:","Instruction format:",pkt.inst_format,", Operation:",pkt.inst,", First Operand x"+str(pkt.rs1),", Immediate value ",pkt.ImmI,", Destination Register x"+str(pkt.rd))
      print("DECODE:","Read Registers:","x"+str(pkt.rs1)+"="+str(pkt.op1))

      
    elif opcode=="0100011":
      pkt.inst_format = "S"
      control.controlStore() #control
      if(funct3==0):
        pkt.inst="sb"
      elif(funct3==1):
        pkt.inst="sh"
      elif(funct3==2):
        pkt.inst="sw"
    
      print("DECODE:","Instruction format:",pkt.inst_format,", Operation:",pkt.inst,", First Operand x"+str(pkt.rs1),", Second Operand x"+str(pkt.rs2),", Immediate value ",pkt.ImmS)
      print("DECODE:","Read Registers:","x"+str(pkt.rs1)+"="+str(pkt.op1),", x"+str(pkt.rs2)+"="+str(pkt.op2))

    elif opcode=="1100011":
      pkt.inst_format = "B"
      control.controlBtype() #control
      if(funct3==0):
        pkt.inst="beq"
      elif(funct3==1):
        pkt.inst="bne"
      elif(funct3==4):
        pkt.inst="blt"
      elif(funct3==5):
        pkt.inst="bge"
      lock.BranchinDE = True
      print("DECODE:","Instruction format:",pkt.inst_format,", Operation:",pkt.inst,", First Operand x"+str(pkt.rs1),", Second Operand x"+str(pkt.rs2),", Immediate value ",pkt.ImmB)
      print("DECODE:","Read Registers:","x"+str(pkt.rs1)+"="+str(pkt.op1),", x"+str(pkt.rs2)+"="+str(pkt.op2))
    
    elif opcode=="1101111":
      pkt.inst_format = "J"
      control.controlJal() #Control
      pkt.inst="jal"

      print("DECODE:","Instruction format:",pkt.inst_format,", Operation:",pkt.inst,", Immediate value ",pkt.ImmJ,", Destination Register x"+str(pkt.rd))


    elif opcode=="1100111":
      pkt.inst_format = "I"
      control.controlJalr()
      pkt.inst="jalr"

      print("DECODE:","Instruction format:",pkt.inst_format,", Operation:",pkt.inst,", First Operand x"+str(pkt.rs1),", Immediate value ",pkt.ImmI,", Destination Register x"+str(pkt.rd))
      print("DECODE:","Read Registers:","x"+str(pkt.rs1)+"="+str(pkt.op1))


    elif opcode=="0110111":
      control.controlLui() #Control
      pkt.inst_format = "U"
      pkt.inst="lui"

      print("DECODE:","Instruction format:",pkt.inst_format,", Operation:",pkt.inst,", Immediate value ",pkt.ImmU,", Destination Register x"+str(pkt.rd))

    
    elif opcode=="0010111":
      control.controlAuipc() #Control
      pkt.inst_format = "U"
      pkt.inst="auipc"

      print("DECODE:","Instruction format:",pkt.inst_format,", Operation:",pkt.inst,", Immediate value ",pkt.ImmU,", Destination Register x"+str(pkt.rd))

    if(knob.knob1==1):
      #Saving required results to pipeline registers
      DE_EX['PC']=IF_DE['PC']
      DE_EX['control'] = {'isBranch':control.isBranch,'RFWrite':control.RFWrite,'OP2Select':control.OP2Select,'ALUOp':control.ALUOp,'MemOP':control.MemOP,'ResultSelect':control.ResultSelect,'BranchTargetSet':control.BranchTargetSet}
      if(lock.Branch==True):
        DE_EX['control']['isBranch']=1
        control.isBranch=1
      DE_EX['ImmB']=pkt.ImmB
      DE_EX['ImmJ']=pkt.ImmJ
      DE_EX['ImmI']=pkt.ImmI
      DE_EX['ImmS']=pkt.ImmS
      DE_EX['ImmU']=pkt.ImmU
      DE_EX['op1']=pkt.op1
      DE_EX['op2']=pkt.op2
      DE_EX['inst_format'] =pkt.inst_format
      DE_EX['inst']=pkt.inst
      DE_EX['rd'] = pkt.rd
      DE_EX['rs1'] = pkt.rs1
      DE_EX['rs2'] = pkt.rs2
      DE_EX['opcode'] = opcode
      DE_EX['inst_encoding'] = IF_DE['inst_encoding'] 

      if(DE_EX['inst_format'] == 'B' and Branch.BTB.get(DE_EX['PC'])==None):
        #This Branch has been encountered for the first time
        Branch.BTB[DE_EX['PC']] = [pkt.ImmB,Branch.counter]

      print("DECODE => Instruction No."+str(((IF_DE['PC']//4) + 1)))