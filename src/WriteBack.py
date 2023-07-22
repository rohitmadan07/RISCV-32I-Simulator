from include import *

def write_back(MA_WB={}):
  #MA_WB -> pipeline register from which we read

  if(knob.knob2==1 and lock.LoadUseWBStall==True):
    lock.LoadUseWBStall=False
    stat.TotalStalls = stat.TotalStalls+1
    stat.DataStalls+=1
    print("WRITEBACK: NO OPERATION (BUBBLE) Because of Load Use Data Hazard")
    return

  if(lock.StallMA==True ):
    if(lock.controlHazard==True): stat.ControlStalls+=1
    else: stat.DataStalls+=1
    lock.StallWB=True
    stat.TotalStalls = stat.TotalStalls+1
    print("WRITEBACK: NO OPERATION (BUBBLE)")
    return

  if(lock.StallWB==True):
    if(lock.controlHazard==True): stat.ControlStalls+=1
    else: stat.DataStalls+=1
    stat.TotalStalls = stat.TotalStalls+1
    print("WRITEBACK: NO OPERATION (BUBBLE)")
    return

  if(knob.knob1==1):
    if((MA_WB['inst_format']=='B' or MA_WB['inst'] in ['jal','jalr']) and lock.controlHazard==True):
      lock.StallDE=False
      lock.controlHazard=False

    pkt.ALUResult = MA_WB['ALUResult']
    pkt.LoadData = MA_WB['LoadData']
    # pkt.PC = MA_WB['PC']
    pkt.ImmU = MA_WB['ImmU']
    control.RFWrite = MA_WB['control']['RFWrite']
    control.ResultSelect = MA_WB['control']['ResultSelect']
    pkt.rd = MA_WB['rd']


  if control.RFWrite == 1:

    if control.ResultSelect ==0:
      mem.RegisterFile[pkt.rd] = pkt.ALUResult

    elif control.ResultSelect ==1:
      mem.RegisterFile[pkt.rd] = pkt.LoadData

    elif control.ResultSelect ==2:
      mem.RegisterFile[pkt.rd] = pkt.ImmU

    elif control.ResultSelect ==3:
      if(knob.knob1==0):
        mem.RegisterFile[pkt.rd] = pkt.PC+4
      else:
        mem.RegisterFile[pkt.rd] = MA_WB['PC']+4
    if(knob.knob1==1):
      print("WRITEBACK: Writeback to register x"+str(pkt.rd),"is",mem.RegisterFile[pkt.rd],"=> Instruction No. "+ str((MA_WB['PC']//4) + 1))
    else:
      print("WRITEBACK: Writeback to register x"+str(pkt.rd),"is",mem.RegisterFile[pkt.rd])
    if pkt.rd==lock.StallRegister: 
      lock.Writing = True #jis register ki wjh se stall hua tha tb hi writing ko true krunga
      lock.writeToStallRegister=True
  else:
    if(knob.knob1==1):
      print("WRITEBACK: No Writeback operation => Instruction No. "+ str(((MA_WB['PC']//4) + 1)))
    else:
      print("WRITEBACK: No Writeback operation")
    pass #Writeback is Disabled
    
