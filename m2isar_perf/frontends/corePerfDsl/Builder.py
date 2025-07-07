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
        top.setArchitecture(self.dictionary.getArchitectureInfo())
        top.assignTraceValues(self.dictionary.traceValues.values())
        top.assignInstructions(self.dictionary.instructions.values())
        
        # Assign microactions and trace-value-assignments which are defined via the ALL and REST keywords
        # Assign unique ID to every instruction
        instrId = 0
        for instr_name, instr in self.dictionary.instructions.items():

            # ALL
            [uA_i.linkInstruction(instr) for uA_i in self.dictionary.ALL_microactions]
            instr.traceValueAssignments.extend(self.dictionary.ALL_traceValueAssignments)

            # REST
            if instr_name not in self.dictionary.instrMicroactionMapped:
                [uA_i.linkInstruction(instr) for uA_i in self.dictionary.REST_microactions]
            if instr_name not in self.dictionary.instrTraceValueMapped:
                instr.traceValueAssignments.extend(self.dictionary.REST_traceValueAssignments)

            # Switch name of default instruction
            if instr_name == Defs.KEYWORD_REST:
                instr.name = Defs.DEFAULT_INSTR_NAME
                
            # Assign unique identifier to every instruction
            instr.identifier = instrId
            instrId += 1
            
        # Finalize the variants and add to top (structural model)
        for model_name in self.dictionary.variants.keys():
                
            dictionary_cpy = self.dictionary.getVariantCopy()            
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
                    raise RuntimeError(f"Variant {variant.name} does not assign a microaction to virtual microaction {uA.virtualAlias}")
                else:
                    for res_i in uA.getResources():
                        if res_i.name == "":
                            raise RuntimeError(f"Variant {variant.name} does not assign a resource to virtual resource {res.virtualAlias}")
                        
            # Link required models used as resource models to variant
            for uA in variant.getAllMicroactions():
                for res_i in uA.getResources():
                    if (resModel:=res_i.resourceModel) is not None:
                        variant.addResourceModel(resModel)

            # Establish link from Connectors to (Connector)Models 
            # Check that (Connector)Model out-connectors are unique (i.e. no connector "driven" by more than one external model)
            outConnectors = []
            for conModel_i in variant.getAllConnectorModels():
                for con_i in conModel_i.getInConnectors():
                    con_i.connectorModel = conModel_i
                for con_i in conModel_i.getOutConnectors():
                    if con_i in outConnectors:
                        raise RuntimeError(f"Connector {outCon_i.name} set by more than one (Connector)Model.")
                    else:
                        con_i.connectorModel = conModel_i
                        outConnectors.append(con_i)

            # Establish link between stages and pipelines (parent components, blocking pipelines)
            variant.resolvePipelineStructure()
                
            # Add finalized variant to TopModel
            top.addVariant(variant)
            
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
