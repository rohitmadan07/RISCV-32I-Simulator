class BranchPred:
    '''
    1 Bit Branch Prediction 

    Branch Target Buffer
    Has a Counter that stores values:
    0 --> Branch will not be taken
    1 --> Branch will be taken

    If in the previous iteration the Branch was taken, then 1 will be stored in the Branch target Buffer
    corresponding to the specific branch instruction (Denoted by its encoding). 
    It means the BranchTarget will be fetched instead of PC+4, when that specific branch is in the Decode Stage
    If this turns out to be Incorrect when we execute the Branch, then the BTB will be updated to 0 and we will cancel
    the BranchTarget instruction's further processing

    Branch Target Buffer (BTB) Structure:-
    It is a dictionary (map) with-
    key = address of the Branch Instruction 
    value = Two element array
            1. Branch Target for that Branch (ImmB)
            2. Counter corresponding to that Branch
    '''

    BTB = {}
    Mispred=0
    counter=1

    def Taken(self,PC):
        if(self.BTB[PC][1] == 0): #Wrong Prediction
            self.Mispred=self.Mispred+1 #Misprediction Count
            self.BTB[PC][1] = 1 #Branch will be taken when this instruction is encountered in the next iteration
        else:
            self.BTB[PC][1] = 1 #Correct Prediction. Counter Remains the same for this branch

    def NotTaken(self,PC):
        if(self.BTB[PC][1] == 1): #Wrong Prediction
            self.Mispred=self.Mispred+1 #Misprediction Count 
            self.BTB[PC][1] = 0 #Branch will not be taken when this instruction is encountered in the next iteration
        else:
            self.BTB[PC][1] = 0 #Correct Prediction

    