class Knob:
    knob1,knob2,knob3,knob4,knob5=[0]*5
    instrNoInp=4 #For Knob5
    if_de,de_ex,ex_ma,ma_wb =[{}]*4 #For storing state of specific instruction for knob5
    def turnOnKnob(self,knobNo):
        if(knobNo==1): self.knob1=1 #Turning it on
        elif(knobNo==2): self.knob2=1
        elif(knobNo==3): self.knob3=1
        elif(knobNo==4):self.knob4=1
        elif(knobNo==5):self.knob5=1