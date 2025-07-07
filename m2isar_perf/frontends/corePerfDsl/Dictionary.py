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

class UnresolvedReference:

    def __init__(self, name_, type_, line_=0):
        #self.name = "UNRESOLVED_REFERENCE_" + name_
        self.name = name_
        self.instanceType = type_
        self.line = line_

    def reportError(self):
        line = "?" if self.line == 0 else self.line
        print(f"ERROR [Line: {line}]: Could not resolve reference {self.name} of type {self.instanceType}. No such instance.")

    def getName(self):
        return self.name

    def getType(self):
        return self.instanceType

    def getLine(self):
        return self.line
    
class InstructionGroup:

    def __init__(self):
        self.name = ""
        self.instructions = []

    def addInstruction(self, instr):
        self.instructions.append(instr)

class Architecture:

    def __init__(self):
        self.name = ""
        self.isa = ""
        
class Dictionary():
    
    def __init__(self):

        ## COMPONENT DICTIONARIES: Components directly related to the StructuralModel ##
        
        # Components owned by variants
        self.variants = {}
        self.pipelines = {}
        self.stages = {}
        self.microactions = {}
        self.connectors = {}
        self.resources = {}
        self.models = {}
        #self.resourceModels = {}
        #self.connectorModels = {}        
        
        # Common components
        self.traceValues = {}
        self.instructions = {}

        
        ## SUPPORT MEMBERS: Objects, list, dicts used during construction of StructuralModel ##
        
        # List of used component names, to avoid dublicates
        self.nameList = []

        # Alias assignments
        self.microactionAssignments = {}
        self.resourceAssignments = {}

        # Instruction container to fit CorePerfDSL references
        self.instructionsGroups = {}

        # Container to keep architecture information
        self.architecture = None
        
        # Lists of mapped instructions (used to map REST instructions)
        self.instrMicroactionMapped = []
        self.instrTraceValueMapped = []

        # Lists to track microactions + traceValueAssignments assigned to ALL/REST instructions 
        self.ALL_microactions = []
        self.ALL_traceValueAssignments = []
        self.REST_microactions = []
        self.REST_traceValueAssignments = []

        # Dummy instructions for reference look-up to ALL and REST keyword
        self.ALL_Instruction = StructuralModel.Instruction()
        self.ALL_Instruction.name = Defs.KEYWORD_ALL
        self.REST_Instruction = StructuralModel.Instruction()
        self.REST_Instruction.name = Defs.KEYWORD_REST

        
    ## INTERFACE FUNCTIONS: BUILDER ##

    def getVariantCopy(self):
        """
        Creates a deep-copy of the dictionary.
        Common components (i.e.: TraceValues, Instructions) are excluded.
        NOTE: Support members are indeed copied. Use at your own risk.

        Returns:
        Dictionary: New instance of the dictionary.
        """

        # Exclude common components from deep-copy
        memo_instr = {id(obj): obj for obj in self.instructions.values()}
        memo_trVals = {id(obj): obj for obj in self.traceValues.values()}

        memo = {**memo_instr, **memo_trVals}
        return copy.deepcopy(self, memo)

    def getArchitectureInfo(self):
        if self.architecture is not None:
            return (self.architecture.name, self.architecture.isa)
        print(f"WARNING: No Architecture component defined!")
        return ("","") 

    ## INTERFACE FUNCTIONS: EXTRACTOR ##
    
    def addConnector(self, name_):
        con = StructuralModel.Connector()
        con.name = name_
        self.__addInstance(con, "Connector")

    def addTraceValue(self, name_):
        trVal = StructuralModel.TraceValue()
        trVal.name = name_
        self.__addInstance(trVal, "TraceValue")
        
    def addConnectorModel(self, name_, link_, inCons_, outCons_, trVals_):
        model = StructuralModel.Model()
        model.name = name_
        model.link = self.__convertString(link_)
        model.traceValues = trVals_
        model.inConnectors = inCons_
        model.outConnectors = outCons_
        self.__addInstance(model, "Model")
        
    def addResourceModel(self, name_, link_, trVals_):
        model = StructuralModel.Model()
        model.name = name_
        model.link = self.__convertString(link_)
        model.traceValues = trVals_
        self.__addInstance(model, "Model")
        
    def addModel(self, name_, link_, trVals_=[], inCons_=[], outCons_=[], isConfigurable_=False):
        model = StructuralModel.Model()
        model.name = name_
        model.link = self.__convertString(link_)
        model.traceValues = trVals_
        model.inConnectors = inCons_
        model.outConnectors = outCons_
        model.isConfig = isConfigurable_

        self.__addInstance(model, "Model")
        
    def addResource(self, name_, delay_=0, model_=None):
        res = StructuralModel.Resource()
        res.name = name_
        if((delay_ != 0) and (model_ != None)):
            raise TypeError("Cannot add resource %s with both static (%d) and dynamic (%s) delay" %(name_, delay_, model_.name))
        else:
            res.delay = delay_
            res.resourceModel = model_
        self.__addInstance(res, "Resource")

    def addVirtualResource(self, virAlias_):
        vRes = StructuralModel.Resource()
        vRes.virtualAlias = virAlias_
        self.__addInstance(vRes, "Resource")

    def addMicroaction(self, name_, refs_):
        uAction = StructuralModel.Microaction()
        uAction.name = name_

        combinationError = False

        # NOTE: Below we only check type of first referrence for each group of compoents.
        # Extractor must make sure that a group of components only contains components of one type!
        
        # Case: inCon -> res -> outCon
        if len(refs_) == 3:
            if type(refs_[0][0]) is StructuralModel.Connector:
                uAction.inConnectors = refs_[0]
            else:
                combinationError = True
            if type(refs_[1][0]) is StructuralModel.Resource:
                uAction.resources = refs_[1]
            else:
                combinationError = True
            if type(refs_[2][0]) is StructuralModel.Connector:
                uAction.outConnectors = refs_[2]
            else:
                combinationError = True

        # Cases: (inCon -> res) or (res -> outCon)
        elif len(refs_) == 2:
            # Case: (inCon -> res)
            if type(refs_[0][0]) is StructuralModel.Connector:
                uAction.inConnectors = refs_[0]
                if type(refs_[1][0]) is StructuralModel.Resource:
                    uAction.resources = refs_[1]
                else:
                    combinationError = True
            # Case: (res -> outCon)
            elif type(refs_[0][0]) is StructuralModel.Resource:
                uAction.resources = refs_[0]
                if type(refs_[1][0]) is StructuralModel.Connector:
                    uAction.outConnectors = refs_[1]
                else:
                    combinationError = True
                    
        # Cases: (inCon) or (res)
        elif len(refs_) == 1:
            # Case: (inCon)
            if type(refs_[0][0]) is StructuralModel.Connector:
                uAction.inConnectors = refs_[0]
            # Case: (res)
            elif type(refs_[0][0]) is StructuralModel.Resource:
                uAction.resources = refs_[0]
        else:
            raise RuntimeError(f"Function addMicroaction for {name_} called with illegal number of references ({len(refs)})")

        if combinationError:
            raise RuntimeError(f"Function addMicroaction for {name_} called with illegal combination of connectors and resources)")

        self.__addInstance(uAction, "Microaction")
        
    def addVirtualMicroaction(self, virAlias_):
        vuAction = StructuralModel.Microaction()
        vuAction.virtualAlias = virAlias_
        self.__addInstance(vuAction, "Microaction")        
        
    def addStage(self, name_, paths_, capacity_, hasOutputBuffer_):
        stage = StructuralModel.Stage()
        stage.name = name_
        stage.paths = paths_
        stage.capacity = capacity_
        stage.hasOutputBuffer = hasOutputBuffer_
        self.__addInstance(stage, "Stage")

    def addPipeline(self, name_, components_, isParallel_, blockPipelines_):
        pipe = StructuralModel.Pipeline()
        pipe.name = name_
        pipe.components = components_
        pipe.isParallel = isParallel_
        pipe.blockPipelines = blockPipelines_
        self.__addInstance(pipe, "Pipeline")

    def addVariant(self, name_, pipe_, conModels_, resAssigns_, uActionAssigns_):
        variant = StructuralModel.Variant()
        variant.name = name_
        variant.pipeline = pipe_
        for model_i in conModels_:
            variant.addConnectorModel(model_i)
        self.__addInstance(variant, "Variant")
        
        self.resourceAssignments[name_] = resAssigns_
        self.microactionAssignments[name_] = uActionAssigns_

    def addInstructionGroup(self, name_, instructions_):
        gr = InstructionGroup()
        gr.name = name_

        for instr_name in instructions_:
            if type(self.getInstance(instr_name, "Instruction")) is not UnresolvedReference:
                instr = self.getInstance(instr_name, "Instruction")
            else:
                self.addInstruction(instr_name)
                instr = self.getInstance(instr_name, "Instruction")
            instr.addGroupName(gr.name)
            gr.addInstruction(instr)

        self.__addInstance(gr, "InstructionGroup")
                
    def addInstruction(self, name_):
        instr = StructuralModel.Instruction()
        instr.name = name_
        self.__addInstance(instr, "Instruction")

    def addArchitecture(self, name_, isa_):
        if self.architecture is None:
            self.architecture = Architecture()
            self.architecture.name = self.__convertString(name_)
            self.architecture.isa = self.__convertString(isa_)
        else:
            print(f"WARNING: Re-definition of Architecture (name:{name_}, isa:{isa_}) is ignored!")
        
    def mapMicroactions(self, instrOrGroup_, microactions_):
        if type(instrOrGroup_) is InstructionGroup:
            for instr_i in instrOrGroup_.instructions:
                self.__linkMicroactionsToInstruction(instr_i, microactions_)
        elif type(instrOrGroup_) is StructuralModel.Instruction:
            self.__linkMicroactionsToInstruction(instrOrGroup_, microactions_)
        else:
            raise TypeError("Function mapMicroactions called with illegal instance of type %s" % type(instrOrGroup_))

    def mapTraceValues(self, instrOrGroup_, traceValMap_):
        if type(instrOrGroup_) is InstructionGroup:
            for instr in instrOrGroup_.instructions:
                self.__addTraceValuesToInstruction(instr, traceValMap_)
        elif type(instrOrGroup_) is StructuralModel.Instruction:
            self.__addTraceValuesToInstruction(instrOrGroup_, traceValMap_)
        else:
            raise TypeError("Function mapTraceValues called with illegal instance of type %s" % type(instrOrGroup_))

    def resolveStages(self):
        for stage_i in self.stages.values():
            self.__resolveReferenceList(stage_i.getPaths())

    def getInstance(self, name_, type_, line_=0):
        subDict = self.__getSubDictionary(type_)
        try:
            inst = subDict[name_]
        except KeyError:
            return UnresolvedReference(name_, type_, line_)
        return subDict[name_]
    
    def isVirtual(self, inst_):
        if not hasattr(inst_, "virtualAlias"):
            return False
        else:
            if inst_.name == "" and inst_.virtualAlias != "":
                return True
            else:
                return False
        
    ## SUPPORT FUNCTIONS ##

    def __resolveReferenceList(self, list_):
        for i in range(len(list_)):
            ref_i = list_[i]
            if type(ref_i) is UnresolvedReference:
                newRef = self.getInstance(ref_i.getName(), ref_i.getType(), ref_i.getLine())
                if type(newRef) is UnresolvedReference:
                    ref_i.reportError()
                else:
                    list_[i] = newRef
    
    def __getSubDictionary(self, type_):

        if(type_ == "Connector"):
            return self.connectors
        elif(type_ == "TraceValue"):
            return self.traceValues
        elif(type_ == "Model"):
            return self.models
        elif(type_ == "Resource"):
            return self.resources
        elif(type_ == "Microaction"):
            return self.microactions
        elif(type_ == "Stage"):
            return self.stages
        elif(type_ == "Pipeline"):
            return self.pipelines
        elif(type_ == "Variant"):
            return self.variants
        elif(type_ == "Instruction"):
            return self.instructions
        elif(type_ == "InstructionGroup"):
            return self.instructionsGroups
        else:
            raise TypeError("No sub-dictionary of type %s" %type_)
        
    def __addInstance(self, inst_, type_):

        subDict = self.__getSubDictionary(type_)
        
        # Add virtual instance
        if hasattr(inst_, "virtualAlias") and inst_.virtualAlias != "":
            if inst_.virtualAlias in self.nameList:
                return -2 # TODO: Add error handling

            subDict[inst_.virtualAlias] = inst_

        # Add non-virtual instance
        elif inst_.name != "":
            if inst_.name in self.nameList:
                return -1 # TODO: Add error handling

            subDict[inst_.name] = inst_ 
            
        else:
            raise TypeError("Cannot add an instance without name or virtual alias")
            
        return 0


    #def __addMicroactionsToInstruction(self, instr_, microactions_):
    #    instr_.microactions.extend(microactions_)
    #    if (instr_.name != Defs.KEYWORD_ALL) and (instr_.name != Defs.KEYWORD_REST):
    #        self.instrMicroactionMapped.append(instr_.name)

    def __linkMicroactionsToInstruction(self, instr_, microactions_):
        if instr_.name == Defs.KEYWORD_ALL:
            self.ALL_microactions.extend(microactions_)
        elif instr_.name == Defs.KEYWORD_REST:
            self.REST_microactions.extend(microactions_)
        else:
            self.instrMicroactionMapped.append(instr_.name)
            for uA_i in microactions_:
                uA_i.linkInstruction(instr_)

    # def __addTraceValuesToInstruction(self, instr_, traceValueAssigns_):
    # 
    #     for trValAss_i in traceValueAssigns_:
    #         assignment = StructuralModel.TraceValueAssignment()
    #         assignment.traceValue = trValAss_i[0]
    #         assignment.description = self.__convertString(trValAss_i[1])
    #         instr_.traceValueAssignments.append(assignment)
    #     
    #     #instr_.traceValueAssignments.extend(traceValueAssigns_)
    #     if (instr_.name != Defs.KEYWORD_ALL) and (instr_.name != Defs.KEYWORD_REST):
    #         self.instrTraceValueMapped.append(instr_.name)

    def __addTraceValuesToInstruction(self, instr_, trValueAssigns_):
        for trValAss_i in trValueAssigns_:
            assignment = StructuralModel.TraceValueAssignment()
            assignment.traceValue = trValAss_i[0]
            assignment.description = self.__convertString(trValAss_i[1])

            if instr_.name == Defs.KEYWORD_ALL:
                self.ALL_traceValueAssignments.append(assignment)
            elif instr_.name == Defs.KEYWORD_REST:
                # TODO: Is this even legal in the CorePerfDSL?
                self.REST_traceValueAssignments.append(assignment)
            else:
                instr_.traceValueAssignments.append(assignment)
                self.instrTraceValueMapped.append(instr_.name)
            
    
    def __convertString(self, str_):
        return str_.strip('\"')
            
