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

import Instances as inst # TODO: Remove? Only used for InstructionInstance. Create in Description?

import copy

class ModelTree:

    def __init__(self, name_):
        self.name = name_
        self.instructionSet = None
        self.corePerfModel = None

class GraphRewriter:

    def __init__(self, description_):
        self.description = description_
        self.modelTrees = []

    def mapInstructions(self):

        print("Mapping Microactions to Instructions")
        
        # Link microactions to instructions according to mapping
        for map in self.description.microactionMappingList:
            if map.singleInstr:
                map.instr.microactions.extend(map.microactions)
            else:
                for instr_i in map.instrGr.instructions:
                    instr_i.microactions.extend(map.microactions)
                    
        # Resolve [?]-keyword: Rename instruction to default
        if self.description.instructionList.exists("[?]"):
            instr = self.description.instructionList.get("[?]")
            instr.name = "_default_"
    
        # Resolve [ALL]-keyword. Add microactions of [ALL] to all other instructions. Delete [ALL]
        if self.description.instructionList.exists("[ALL]"):
            all_microactions = self.description.instructionList.get("[ALL]").microactions
            for instr_i in self.description.instructionList:
                if instr_i.name != "[ALL]":
                    instr_i.microactions.extend(all_microactions)
                    
            self.description.instructionList.delete("[ALL]")

        # Make sure that CorePerfModels support all required Microactions
        for model in self.description.corePerfModelList:

            supportedMicroactions = []
            
            for st in model.pipeline.stages:
                supportedMicroactions.extend([uA for uA in st.microactions])

            for (vuA, uA) in model.microactionAssignments:
                if vuA in supportedMicroactions:
                    supportedMicroactions.append(uA) # TODO: This might no be necessary. Instruction mapping likely to use virtual instances!?

            for instr in self.description.instructionList:
                for uA in instr.microactions:
                    if uA not in supportedMicroactions:
                        print("ERROR: CorePerfModel %s does not provide Microaction %s. Required by Instruction %s" % (model.name, uA.name, instr.name))
            
    def extractModelTrees(self):
        
        for corePerfModel in self.description.corePerfModelList:

            print("Extracting ModelTree for CorePerfModel %s" % corePerfModel.name)
            
            modelTree = ModelTree(corePerfModel.name)

            cpy_memo = {}
            modelTree.corePerfModel = copy.deepcopy(corePerfModel, cpy_memo)
            modelTree.instructionSet = copy.deepcopy(self.description.instructionList, cpy_memo)
            
            unresolvedVirResources = []
            unresolvedVirMicroactions = []
            unresolvedInConnectors = []
            unresolvedOutConnectors = []
            
            # Find virt. instances and supported microactions
            for st in modelTree.corePerfModel.pipeline.stages:
                for uA in st.microactions:
                    if uA.isVirtual():
                        unresolvedVirMicroactions.append(uA)
                    else:
                        if uA.inConnector is not None:
                            unresolvedInConnectors.append(uA.inConnector)
                        if uA.resource is not None:
                            if uA.resource.isVirtual():
                                unresolvedVirResources.append(uA.resource)
                        if uA.outConnector is not None:
                            unresolvedOutConnectors.append(uA.outConnector)
                                    
            # Resolve virtual instances
            for (vuA, uA) in modelTree.corePerfModel.microactionAssignments:
                vuA.replaceVirtual(uA)
                unresolvedVirMicroactions.remove(vuA)
            for vuA in unresolvedVirMicroactions:
                print("ERROR: CorePerfModel %s does not assign a microaction to virtual microaction %s" % (modelTree.name, vuA.name))
                
                
            for (vRes, res) in modelTree.corePerfModel.resourceAssignments:
                vRes.replaceVirtual(res)
                unresolvedVirResources.remove(vRes)
            for vRes in unresolvedVirResources:
                print("ERROR: CorePerfModel %s does not assign a resource to virtual resource %s" % (modelTree.name, vRes.name))

            # Check that every connector has a connectorModel
            checkInConnectors = copy.copy(unresolvedInConnectors)
            checkOutConnectors = copy.copy(unresolvedOutConnectors)
            for cModel in modelTree.corePerfModel.connectorModels:

                for inCon in cModel.outCons:
                    if inCon in unresolvedInConnectors:
                        unresolvedInConnectors.remove(inCon)
                    elif inCon in checkInConnectors:
                        print("ERROR: CorePerfModel %s: Connector %s connected to ConnectorModel %s but already assigned to another model" % (modelTree.corePerfModel.name, inCon.name, cModel.name))
                    else:
                        print("WARNING: CorePerfModel %s: Connector %s connected to ConnectorModel %s but not to any Microaction" % (modelTree.corePerfModel.name, inCon.name, cModel.name))
                        
                    if inCon in checkOutConnectors:
                        print("ERROR CorePerfModel %s: Connector %s connected as an input to both ConnectorModel %s and an Microactions" % (modelTree.corePerfModel.name, inCon.name, cModel.name))

                for outCon in cModel.inCons:
                    if outCon in unresolvedOutConnectors:
                        unresolvedOutConnectors.remove(outCon)
                    elif outCon in checkOutConnectors:
                        print("ERROR: CorePerfModel %s: Connector %s connected to ConnectorModel %s but already assigned to another model" % (modelTree.corePerfModel.name, outCon.name, cModel.name))
                    else:
                        print("WARNING: CorePerfModel %s: Connector %s connected to ConnectorModel %s but not to any Microaction" % (modelTree.corePerfModel.name, outCon.name, cModel.name))
                        
                    if outCon in checkInConnectors:
                        print("ERROR CorePerfModel %s: Connector %s connected as an output to both ConnectorModel %s and an Microactions" % (modelTree.corePerfModel.name, outCon.name, cModel.name))

            for con in unresolvedInConnectors:
                print("ERROR: CorePerfModel %s does not provide a ConnectorModel for Input-Connector %s" % (modelTree.name, con.name))

            for con in unresolvedOutConnectors:
                print("ERROR: CorePerfModel %s does not provide a ConnectorModel for Output-Connector %s" % (modelTree.name, con.name))
                        
            #Store model tree
            self.modelTrees.append(modelTree)

        
