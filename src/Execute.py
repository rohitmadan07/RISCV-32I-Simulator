from include import *

def execute(DE_EX={},EX_MA={}):
    #DE_EX -> pipeline register from which we read
    #EX_MA -> pipeline register to which we write

    if(knob.knob2==1 and lock.LoadUseEXStall==True):        
        lock.LoadUseDEStall=True
        lock.LoadUseEXStall=False
        lock.LoadUseMAStall=True
        stat.TotalStalls = stat.TotalStalls+1
        stat.DataStalls+=1
        print("EXECUTE: STALLED Because of Load Use Data Hazard")
        return

    if(lock.LoadUseHazard!=True and knob.knob1==1 and lock.Branch==True):
        lock.Branch=False
        lock.StallIF=False  
        lock.ControlHazard() #Agli baar jab ayenge

    if(lock.LoadUseHazard!=True and knob.knob1==1 and DE_EX['inst_encoding']==TerminationCode):
        EX_MA['inst_encoding'] = DE_EX['inst_encoding']
        lock.StallEX=False 
        print("EXECUTE: TERMINATED")
        return

    if(lock.LoadUseHazard!=True and lock.StallDE == True):
        if(lock.controlHazard==True):
            stat.ControlStalls+=1
            if(DE_EX['control']['BranchTargetSet']==0): EX_MA['control']['BranchTarget'] = DE_EX['PC']+pkt.ImmJ 
            else: EX_MA['control']['BranchTarget'] = DE_EX['PC']+pkt.ImmB 
        if(lock.controlHazard!=True): stat.DataStalls+=1
        lock.StallEX = True
        stat.TotalStalls = stat.TotalStalls+1
        print("EXECUTE: NO OPERATION (BUBBLE)")
        #Piche se instruction hi nhi aaya isliye kuch nhi kr skte
        return
    
    if(lock.LoadUseHazard!=True and lock.StallEX==True):
        stat.DataStalls+=1 #??
        stat.TotalStalls = stat.TotalStalls+1
        print("EXECUTE: NO OPERATION (BUBBLE)")
        return

    else:
        lock.StallMA=False
        if (knob.knob1==0): 
            alu.inp1 = pkt.op1
            if(control.OP2Select == 0): alu.inp2 = pkt.ImmS
            elif (control.OP2Select == 1): alu.inp2 = pkt.ImmI
            else: alu.inp2 = pkt.op2
        else: #Pipelined Executiom
            alu.inp1 = DE_EX['op1']
            if(DE_EX['control']['OP2Select'] == 0): alu.inp2 = DE_EX['ImmS']
            elif (DE_EX['control']['OP2Select'] == 1): alu.inp2 = DE_EX['ImmI']
            else: alu.inp2 = DE_EX['op2']
            pkt.inst = DE_EX['inst'] #Reading the instrcution from the previous stage Pipeline register and updating the instruction packet
            pkt.inst_format = DE_EX['inst_format']

        if(knob.knob2==1):#Forwarding
            if(frwd.forwardInp1==2):
                if(EX_MA['inst']=='lui'):
                    alu.inp1=EX_MA['ImmU']
                elif(lock.LoadUseHazard==True): alu.inp1 = mem.RegisterFile[EX_MA['rs1']]
                else: alu.inp1 = EX_MA['ALUResult']  
            elif(frwd.forwardInp2==2): 
                if(EX_MA['inst']=='lui'):
                    alu.inp2=EX_MA['ImmU']
                elif(lock.LoadUseHazard==True): alu.inp2 = mem.RegisterFile[DE_EX['rs2']]
                else: alu.inp2 = EX_MA['ALUResult']
            if(frwd.forwardInp1==3):
                alu.inp1 = mem.RegisterFile[DE_EX['rs1']] 
            elif(frwd.forwardInp2==3):  
                alu.inp2 = mem.RegisterFile[DE_EX['rs2']]
            if(lock.LoadUseHazard==True):
                print("Forwarding from MA_WB of WB to EX")
            
            frwd.ResetEX()
            lock.LoadUseHazard=False

        if(pkt.inst == "add" or pkt.inst=="addi" or pkt.inst in ["lb","lh","lw"] or pkt.inst_format=="S" or pkt.inst == "jalr" ):
            control.ALUOp = "addition"
            pkt.ALUResult = alu.addition()
            print("EXECUTE: ADD", alu.inp1, "and", alu.inp2)
            stat.TotalALUinst=stat.TotalALUinst+1

        elif(pkt.inst == "sub" or pkt.inst == "slt" or pkt.inst_format == "B"):
            control.ALUOp = "subtraction"
            result = alu.subtraction()
            stat.TotalALUinst=stat.TotalALUinst+1

            if(pkt.inst=="sub"):
                pkt.ALUResult = result
            elif (pkt.inst == "slt"):
                pkt.ALUResult = 1 if result<0 else 0
            else: #Branch Instructions
                if(pkt.inst=="beq"):
                    pkt.ALUResult = 1 if result==0 else 0 #1-> Branch will be taken
                elif(pkt.inst=="bne"):
                    pkt.ALUResult = 1 if result!=0 else 0
                elif(pkt.inst=="bge"):
                    pkt.ALUResult = 1 if result>=0 else 0
                elif(pkt.inst=="blt"):
                    pkt.ALUResult = 1 if result<0 else 0
                control.isBranch = 1 if pkt.ALUResult==1 else 0  
                stat.TotalControlInst=stat.TotalControlInst+1    
            print("EXECUTE: SUBTRACT", alu.inp2, "from", alu.inp1)

        elif(pkt.inst == "sll"):
            control.ALUOp = "left shift"
            pkt.ALUResult = alu.leftshift()
            stat.TotalALUinst=stat.TotalALUinst+1
            print("EXECUTE: LEFT SHIFT", alu.inp1, "by", alu.inp2, "bits")

        elif(pkt.inst == "xor"):
            control.ALUOp = "xor"
            pkt.ALUResult = alu.xor()
            stat.TotalALUinst=stat.TotalALUinst+1

            print("EXECUTE: XOR operation on", alu.inp1, "and", alu.inp2)

        elif(pkt.inst == "srl" or pkt.inst == "sra"):
            if(pkt.inst=="srl"): pkt.ALUResult = alu.srl(); print("EXECUTE: LOGICAL RIGHT SHIFT", alu.inp1, "by", alu.inp2, "bits")
            else: pkt.ALUResult = alu.sra(); print("EXECUTE: ARITHMETIC RIGHT SHIFT", alu.inp1, "by", alu.inp2, "bits")
            stat.TotalALUinst=stat.TotalALUinst+1

        elif(pkt.inst == "or" or pkt.inst=="ori"):
            pkt.ALUResult = alu.inp1 | alu.inp2
            print("EXECUTE: OR operation on", alu.inp1, "and", alu.inp2)
            stat.TotalALUinst=stat.TotalALUinst+1

        elif(pkt.inst == "and" or pkt.inst=="andi"):
            pkt.ALUResult = alu.inp1 & alu.inp2
            print("EXECUTE: AND operation on", alu.inp1, "and", alu.inp2)
            stat.TotalALUinst=stat.TotalALUinst+1

        elif(pkt.inst == "jal"):
            stat.TotalControlInst=stat.TotalControlInst+1    
            print("EXECUTE: jal operation") 
            pass #No ALU Operation

        elif(pkt.inst == "lui"):
            print("EXECUTE: lui operation")
            pass

        elif(pkt.inst == "auipc"):
            pkt.ALUResult = pkt.PC + pkt.ImmU
            print("EXECUTE: auipc operation")

        else:
            print("Invalid instruction type\n")

        #PC Update and Branch Target Calculations

        if(knob.knob1==0):
            if(control.BranchTargetSet==0): pkt.BranchTarget = pkt.PC+pkt.ImmJ
            else: pkt.BranchTarget = pkt.PC+pkt.ImmB
            
            if (control.isBranch ==0): pkt.PC = pkt.PC + 4
            elif(control.isBranch ==1): pkt.PC = pkt.BranchTarget
            else: pkt.PC = pkt.ALUResult

        else: #Pipelined
            EX_MA['PC'] = DE_EX['PC']
            EX_MA['control'] = DE_EX['control']
            if(DE_EX['control']['BranchTargetSet']==0): EX_MA['control']['BranchTarget'] = DE_EX['PC']+pkt.ImmJ 
            else: EX_MA['control']['BranchTarget'] = DE_EX['PC']+pkt.ImmB 
            pkt.BranchTarget = EX_MA['control']['BranchTarget']
            EX_MA['ALUResult'] = pkt.ALUResult
            EX_MA['op1'] = DE_EX['op1']
            EX_MA['op2'] = DE_EX['op2']
            EX_MA['inst']=pkt.inst
            EX_MA['ImmU'] = DE_EX['ImmU']
            EX_MA['ImmI'] = DE_EX['ImmI']
            EX_MA['ImmS'] = DE_EX['ImmS']
            EX_MA['rd'] = DE_EX['rd']
            EX_MA['rs1'] = DE_EX['rs1']
            EX_MA['rs2'] = DE_EX['rs2']
            EX_MA['inst_encoding'] = DE_EX['inst_encoding'] 
            EX_MA['inst_format'] = DE_EX['inst_format'] 
            EX_MA['opcode'] = DE_EX['opcode']
            
            if(control.isBranch==1):
                lock.Branch=True
                Branch.Taken(EX_MA['PC']) #Branch will be taken and checking the corresponding prediction for this branch in BTB
                EX_MA['control']['isBranch']=1
            
            else: 
                EX_MA['control']['isBranch']=0
                if(EX_MA['inst_format']=='B'):
                    Branch.NotTaken(EX_MA['PC']) #Branch will not be taken and checking the corresponding prediction for this branch in BTB

            if(EX_MA['inst_format']=='B' and control.isBranch!=1):
                lock.BranchNotTaken=True
            
            stat.TotalinstEX = stat.TotalinstEX+1
            print("EXECUTE => Instruction No. "+str(((DE_EX['PC']//4) + 1)))