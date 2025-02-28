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

from meta_models.structural_model import StructuralModel
from . import Defs

class Builder():

    def __init__(self, dictionary_):

        self.dictionary = dictionary_
        
    def buildTopModel(self):

        top = StructuralModel.StructuralModel()

        # Establish connections between stages and pipelines (parents, blocking)
        
        
        # Assign microactions and trace-value-assignments which are defined via the ALL and REST keywords
        instrId = 0
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

            # Assign unique identifier to every instruction
            instr.identifier = instrId
            instrId += 1
                
        # Finalize the variants and add to top (structural model)
        for model_name in self.dictionary.variants.keys():

            # Assign all instructions to each variant
            for instr_i in self.dictionary.instructions.values():
                self.dictionary.variants[model_name].instructions.append(instr_i)
                
            # Create variant instance with unique child objects
            # NOTE: Make deep copy of dictionary, as we also need to copy non-virtual resources/microactions that are assigned to the current model later on
            dictionary_cpy = copy.deepcopy(self.dictionary)
            variant = dictionary_cpy.variants[model_name]
            
            # Resolve virtual microactions
            for uActAss in dictionary_cpy.microactionAssignments[variant.name]:                
                viruAct = uActAss[0]
                uAct = uActAss[1]
                viruAct.assign(uAct)

            # Resolve virtual resources
            for resAss in dictionary_cpy.resourceAssignments[variant.name]:
                virRes = resAss[0]
                res = resAss[1]
                virRes.assign(res)
                
            # Check that all virtual components of CorePerfModel have been resolved and link resource models to corePerfModel
            for uA in variant.getAllMicroactions():
                if uA.name == "":
                    print("ERROR: Variant %s does not assign a microaction to virtual microaction %s" % (variant.name, uA.virtualAlias)) # TODO: Add proper error handling
                else:
                    for res_i in uA.getResources():
                        if res_i.name == "":
                            raise RuntimeError(f"Variant {variant.name} does not assign a resource to virtual resource {res.virtualAlias}")
                        else:
                            if (resModel:=res_i.resourceModel) is not None:
                                variant.resourceModels.append(resModel)
            
            # Establish link from Connectors to ConnectorModel & set connector type
            #   (Remember: Connector type is set seen from perspective of microaction.
            #    I.e. a connector connected to input of connectorModel is of type CON_TYPE_OUT,
            #    and vice versa)
            for conModel in variant.connectorModels:
                for inCon in conModel.inConnectors:
                    inCon.connectorModel = conModel
                    self.__setConnectorType(inCon, Defs.CON_TYPE_OUT, conModel, variant)
                for outCon in conModel.outConnectors:
                    outCon.connectorModel = conModel
                    self.__setConnectorType(outCon, Defs.CON_TYPE_IN, conModel, variant)

            # Check that there are no connectors without a connector model & that connector type matches microaction
            for uA in variant.getAllMicroactions():
                self.__checkConnector(uA.getInConnectors(), Defs.CON_TYPE_IN, uA, variant)
                self.__checkConnector(uA.getOutConnectors(), Defs.CON_TYPE_OUT, uA, variant)

            # Establish link between stages and pipelines (parent components, blocking pipelines)
            variant.resolvePipelineStructure()
                
            # Add finalized variant to TopModel
            top.variants.append(variant)

        return top
                    
    # Helper Functions

    def __setConnectorType(self, con_, type_, conModel_, corePerfModel_):
        if con_.connectorType == "":
            con_.connectorType = type_
        else:
            if con_.connectorType != type_:
                print("ERROR: For CorePerfModel %s, Connector %s is not of type %s but connected to input of ConnectorModel %s" % (corePerfModel.name, con_.name, type_, conModel_.name)) # Add proper error handling

    def __checkConnector(self, cons_, type_, uA_, corePerfModel_):
        for con_i in cons_:
            if con_i is not None:
                if con_i.connectorModel is None:
                    raise RuntimeError(f"For CorePerfModel {corePerfModel_.name}, Connector {con_i.name} (in {uA_.name}) is not connected to any ConnectorModel")
                else:
                    if con_i.connectorType != type_:
                        raise RuntimeError(f"For CorePerfModel {corePerfModel_.name}, Connector {con_i.name} is an {type_}-Connecotr for Microaction {uA_.name} and connected to the input of ConnectorModel {con_i.connectorModel.name}")
