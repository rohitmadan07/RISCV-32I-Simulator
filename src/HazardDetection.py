class DataLock:
    #Stall -> NOP -> No Operation performed by the stage in that cycle.
    StallIF,StallDE,StallEX,StallMA,StallWB=[False]*5
    LoadUseIFStall,LoadUseDEStall,LoadUseEXStall,LoadUseMAStall,LoadUseWBStall=[False]*5
    LoadUseHazard=False
    StallRegister = None
    Writing = False #Write Operation happening in the current cycle, cannot read the same register.
    currChange = False
    Branch = False #Branch will be taken or not
    isBranch=False #Branch or not
    writeToStallRegister = False
    controlHazard = False
    dataHazard = False
    BranchNotTaken=False
    BranchinDE=False
    ControlH = 0
    DataH = 0

    def detectLoadUse(self,DE_EX,EX_MA):
        #Returns True if Load Use Data Hazard is Detected
        if(EX_MA['opcode']=='0000011' and DE_EX['opcode'] != '0100011'):
            #EX_MA-> load instruction DE_EX-> Use instruction apart from store
            print("LOAD USE DATA HAZARD DETECTED")
            self.LoadUseEXStall=True
            return True
        return False

    def detectRAW(self,DE_EX,EX_MA,MA_WB,knob,frwd):
        flag = True
        #Earlier Instruction (we need to give preference to Earlier instruction.)   
        if(DE_EX!={} and EX_MA!={} and EX_MA['opcode']!='1100011' and ((DE_EX['opcode']!='1101111' and DE_EX['rs1'] == EX_MA['rd']) or (DE_EX['opcode'] not in ['1101111','0010011','0000011','1100111'] and DE_EX['rs2'] == EX_MA['rd']))):
            if(knob.knob2==1):#Forwarding
                #Load Use Data Hazard
                if(DE_EX['rs1'] == EX_MA['rd']):
                    frwd.forwardInp1=2
                    self.LoadUseHazard=self.detectLoadUse(DE_EX,EX_MA)
                    if(self.LoadUseHazard==False):
                        print("Will Forward from EX_MA of MA to EX from I"+str((EX_MA['PC']//4)+1)+" to I"+str((DE_EX['PC']//4)+1))
                    flag = False #No need to check 2nd data hazard condition
                else:
                    if(DE_EX['opcode']=='0100011'):
                        #Store After Anything Case. EX_MA-> load and DE_EX-> store
                        frwd.forwardDataWrite=2
                        print("Will Forward from MA_WB of WB to MA from I"+str((EX_MA['PC']//4)+1)+" to I"+str((DE_EX['PC']//4)+1))
                    else:
                        frwd.forwardInp2=2
                        self.LoadUseHazard=self.detectLoadUse(DE_EX,EX_MA)
                        if(self.LoadUseHazard==False):
                            print("Will Forward from EX_MA of MA to EX from I"+str((EX_MA['PC']//4)+1)+" to I"+str((DE_EX['PC']//4)+1))
                        flag = False #No need to check 2nd data hazard condition
                

            if(knob.knob1==1 and knob.knob2==0):
                self.StallIF = True
                self.StallDE = True
                self.dataHazard=True
                #self.StallEX = True
                self.StallRegister = EX_MA['rd'] #Jiske wajah se stall hua.. jaise hi yeh available hojaye toh stall hta skte
                print("DECODE: DATA HAZARD Detected at register: x" + str(self.StallRegister)+"between instructions, I"+str((EX_MA['PC']//4)+1)+"and I"+str((DE_EX['PC']//4)+1))

            self.DataH=self.DataH+1

        #Later Instruction
        if(flag and self.writeToStallRegister!=True and DE_EX!={} and MA_WB!={} and MA_WB['opcode']!='1100011' and ((DE_EX['opcode']!='1101111' and DE_EX['rs1'] == MA_WB['rd']) or (DE_EX['opcode'] not in ['1101111','0010011','0000011','1100111'] and DE_EX['rs2'] == MA_WB['rd']))):
            if(knob.knob2==1):#Forwarding
                if(DE_EX['rs1'] == MA_WB['rd']):
                    frwd.forwardInp1=3
                else:
                    frwd.forwardInp2=3
                print("Will Forward from MA_WB of WB to EX from I"+str((MA_WB['PC']//4)+1)+" to I"+str((DE_EX['PC']//4)+1))
            
            if(knob.knob1==1 and knob.knob2==0):
                self.StallIF = True
                self.StallDE = True
                self.dataHazard = True
                #self.StallEX = True
                self.StallRegister = MA_WB['rd'] #Jiske wajah se stall hua.. jaise hi yeh available hojaye toh stall hta skte
                print("DECODE: DATA HAZARD Detected at register: x" + str(self.StallRegister)+"between instructions, I"+str((MA_WB['PC']//4)+1)+"and I"+str((DE_EX['PC']//4)+1))
            
            self.DataH=self.DataH+1
            
        if(self.writeToStallRegister==True):
            self.writeToStallRegister = False

    def ControlHazard(self):
        self.StallDE=True
        self.StallEX=True
        self.controlHazard = True
        self.ControlH=self.ControlH+1
        print("EXECUTE: CONTROL HAZARD: Stalling DE and EX stages")

