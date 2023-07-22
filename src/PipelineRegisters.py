class PipelineRegister:
    #Pipeline register are just to save values in between positive/negative edge trigger of the clock. The instruction packet generated is stored in these registers
    IF_DE ={}
    DE_EX ={}
    EX_MA ={}
    MA_WB ={}

    def flushPipeline(self):
        #Flushing/Emptying all the pipeline registers
        self.IF_DE={}
        self.DE_EX={}
        self.EX_MA={}
        self.MA_WB={}