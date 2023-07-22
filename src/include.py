from Memory import memory
from ControlUnit import Control
from InstructionPacket import Packet
from ALU import ALU
from PipelineRegisters import PipelineRegister
from Knobs import Knob
from HazardDetection import DataLock
from ForwardingUnit import Forwarding
from StatsToPrint import Stats
from BranchPrediction import BranchPred

TerminationCode = 0xFFFFFFFF

mem = memory()
pkt = Packet()
control = Control()
alu = ALU()
pReg = PipelineRegister()
knob = Knob()
lock = DataLock()
frwd = Forwarding()
stat = Stats()
Branch = BranchPred()