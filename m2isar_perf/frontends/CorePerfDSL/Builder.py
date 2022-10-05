# 
# Copyright 2022 Chair of EDA, Technical University of Munich
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#       http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import copy

from metamodel import MetaModel
from . import Defs

class Builder():

    def __init__(self, dictionary_):

        self.dictionary = dictionary_
        
    def buildTopModel(self):

        top = MetaModel.TopModel()
        
        # Assign microactions and trace-value-assignments which are defined via the ALL and REST keywords
        for instr_name, instr in self.dictionary.instructions.items():

            instr.microactions.extend(self.dictionary.ALL_Instruction.microactions)
            instr.traceValueAssignments.extend(self.dictionary.ALL_Instruction.traceValueAssignments)

            if instr_name not in self.dictionary.instrMicroactionMapped:
                instr.microactions.extend(self.dictionary.REST_Instruction.microactions)
            if instr_name not in self.dictionary.instrTraceValueMapped:
                instr.traceValueAssignments.extend(self.dictionary.REST_Instruction.traceValueAssignments)

            if instr_name == Defs.KEYWORD_REST:
                instr.name = Defs.DEFAULT_INSTR_NAME
                instr_name = instr.name # TODO: Only used for the opcode/mask assignment below. Remove?
                
            # TODO / FIXME: Temp workaround! Replace with unique instruction-type-id assignment, to decouple estimator model from CoreDSL2
            if instr_name == "add":
                instr.opcode = "0x00000033"
                instr.mask   = "0xfe00707f"
            elif instr_name == "sub":
                instr.opcode = "0x40000033"
                instr.mask   = "0xfe00707f"
            elif instr_name == "sll":
                instr.opcode = "0x00001033"
                instr.mask   = "0xfe00707f"
            elif instr_name == "xor":
                instr.opcode = "0x00004033"
                instr.mask   = "0xfe00707f"
            elif instr_name == "or":
                instr.opcode = "0x00006033"
                instr.mask   = "0xfe00707f"
            elif instr_name == "and":
                instr.opcode = "0x00007033"
                instr.mask   = "0xfe00707f"
            elif instr_name == "mul":
                instr.opcode = "0x02000033"
                instr.mask   = "0xfe00707f"
            elif instr_name == "rem":
                instr.opcode = "0x02006033"
                instr.mask   = "0xfe00707f"
            elif instr_name == "addi":
                instr.opcode = "0x00000013"
                instr.mask   = "0x0000707f"
            elif instr_name == "sltiu":
                instr.opcode = "0x00003013"
                instr.mask   = "0xfe00707f"
            elif instr_name == "xori":
                instr.opcode = "0x00004013"
                instr.mask   = "0x0000707f"
            elif instr_name == "ori":
                instr.opcode = "0x00006013"
                instr.mask   = "0x0000707f"
            elif instr_name == "andi":
                instr.opcode = "0x00007013"
                instr.mask   = "0x0000707f"
            elif instr_name == "sb":
                instr.opcode = "0x00000023"
                instr.mask   = "0x0000707f"
            elif instr_name == "sh":
                instr.opcode = "0x00001023"
                instr.mask   = "0x0000707f"
            elif instr_name == "sw":
                instr.opcode = "0x00002023"
                instr.mask   = "0x0000707f"
            elif instr_name == "beq":
                instr.opcode = "0x00000063"
                instr.mask   = "0x0000707f"
            elif instr_name == "bne":
                instr.opcode = "0x00001063"
                instr.mask   = "0x0000707f"
            elif instr_name == "blt":
                instr.opcode = "0x00004063"
                instr.mask   = "0x0000707f"
            elif instr_name == "bge":
                instr.opcode = "0x00005063"
                instr.mask   = "0x0000707f"
            elif instr_name == "bltu":
                instr.opcode = "0x00006063"
                instr.mask   = "0x0000707f"
            elif instr_name == "bgeu":
                instr.opcode = "0x00007063"
                instr.mask   = "0x0000707f"
            elif instr_name == "lh":
                instr.opcode = "0x00001003"
                instr.mask   = "0x0000707f"
            elif instr_name == "lw":
                instr.opcode = "0x00002003"
                instr.mask   = "0x0000707f"
            elif instr_name == "lbu":
                instr.opcode = "0x00004003"
                instr.mask   = "0x0000707f"
            elif instr_name == "lhu":
                instr.opcode = "0x00005003"
                instr.mask   = "0x0000707f"
            elif instr_name == "c_beqz":
                instr.opcode = "0x0000c001"
                instr.mask   = "0x0000e003"
            elif instr_name == "c_bnez":
                instr.opcode = "0x0000e001"
                instr.mask   = "0x0000e003"
            elif instr_name == "c_add":
                instr.opcode = "0x00009002"
                instr.mask   = "0x0000f003"
            elif instr_name == "c_addi":
                instr.opcode = "0x00000001"
                instr.mask   = "0x0000e003"
            elif instr_name == "c_slli":
                instr.opcode = "0x00000002"
                instr.mask   = "0x0000f003"
            elif instr_name == "c_addi16sp":
                instr.opcode = "0x00006101"
                instr.mask   = "0x0000ef83"
            elif instr_name == "c_lw":
                instr.opcode = "0x00004000"
                instr.mask   = "0x0000e003"
            elif instr_name == "c_sw":
                instr.opcode = "0x0000c000"
                instr.mask   = "0x0000e003"
            elif instr_name == "c_mv":
                instr.opcode = "0x00008002"
                instr.mask   = "0x0000f003"
            elif instr_name == "c_li":
                instr.opcode = "0x00004001"
                instr.mask   = "0x0000e003"
            elif instr_name == Defs.DEFAULT_INSTR_NAME:
                instr.opcode = "0xffffffff"
                instr.mask   = "0x00000000"
            else:
                print("Unknown instruction: " + instr_name)
                
                
        # Finalize the CorePerfModels and add to TopModel
        for model_name, model in self.dictionary.corePerfModels.items():

            # Assign all instructions to each corePerfModel
            for instr_name, instr in self.dictionary.instructions.items():
                model.instructions.append(instr)
            
            # Create corePerfModel instance with unique child objects
            corePerfModel = copy.deepcopy(model)
            
            # Resolve virtual microactions
            for uActAss in corePerfModel.microactionAssignments:
                viruAct = uActAss[0]
                uAct = uActAss[1]

                viruAct.name = uAct.name
                viruAct.inConnector = uAct.inConnector
                viruAct.resource = uAct.resource
                viruAct.outConnector = uAct.outConnector

            # Resolve virtual resources
            for resAss in corePerfModel.resourceAssignments:
                virRes = resAss[0]
                res = resAss[1]

                virRes.name = res.name
                virRes.delay = res.delay
                virRes.resourceModel = res.resourceModel

            # Check that all virtual components of CorePerfModel have been resolved and link resource models to corePerfModel
            for uA in corePerfModel.getAllMicroactions():
                if uA.name == "":
                    print("ERROR: CorePerfModel %s does not assign a microaction to virtual microaction %s" % (corePerfModel.name, uA.virtualAlias)) # Add proper error handling
                else:
                    res = uA.resource
                    if res is not None:
                        if res.name == "":
                            print("ERROR: CorePerfModel %s does not assign a microaction to virtual microaction %s" % (corePerfModel.name, res.virtualAlias)) # Add proper error handling
                        else:
                            resModel = res.resourceModel
                            if resModel is not None:
                                corePerfModel.resourceModels.append(resModel)
            
            # Establish link from Connectors to ConnectorModel & set connector type
            #   (Remember: Connector type is set seen from perspective of microaction.
            #    I.e. a connector connected to input of connectorModel is of type CON_TYPE_OUT,
            #    and vice versa)
            for conModel in corePerfModel.connectorModels:
                for inCon in conModel.inConnectors:
                    inCon.connectorModel = conModel
                    self.__setConnectorType(inCon, Defs.CON_TYPE_OUT, conModel, corePerfModel)
                for outCon in conModel.outConnectors:
                    outCon.connectorModel = conModel
                    self.__setConnectorType(outCon, Defs.CON_TYPE_IN, conModel, corePerfModel)

            # Check that there are no connectors without a connector model & that connector type matches microaction
            for uA in corePerfModel.getAllMicroactions():
                self.__checkConnector(uA.inConnector, Defs.CON_TYPE_IN, uA, corePerfModel)
                self.__checkConnector(uA.outConnector, Defs.CON_TYPE_OUT, uA, corePerfModel)
                        
            # Add finalized CorePerfModel to TopModel
            top.corePerfModels.append(corePerfModel)

        return top
                    
    # Helper Functions

    def __setConnectorType(self, con_, type_, conModel_, corePerfModel_):
        if con_.connectorType == "":
            con_.connectorType = type_
        else:
            if con_.connectorType != type_:
                print("ERROR: For CorePerfModel %s, Connector %s is not of type %s but connected to input of ConnectorModel %s" % (corePerfModel.name, con_.name, type_, conModel_.name)) # Add proper error handling

    def __checkConnector(self, con_, type_, uA_, corePerfModel_):
        if con_ is not None:
            if con_.connectorModel is None:
                print("ERROR: For CorePerfModel %s, Connector %s (in %s) is not connected to any ConnectorModel" % (corePerfModel_.name, con_.name, uA_.name))
            else:
                if con_.connectorType != type_:
                    print("ERROR: For CorePerfModel %s, Connector %s is an %s-Connecotr for Microaction %s and connected to the input of ConnectorModel %s" % (corePerfModel_.name, con_.name, type_, uA_.name, con_.connectorModel.name))
