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

from metamodel import MetaModel
from . import Defs

class UnresolvedReference:

    def __init__(self, name_):
        self.name = "UNRESOLVED_REFERENCE_" + name_

class InstructionGroup:

    def __init__(self):
        self.name = ""
        self.instructions = []

    def addInstruction(self, instr):
        self.instructions.append(instr)
        
class Dictionary():
    
    def __init__(self):

        self.nameList = []
        
        self.connectors = {}
        self.traceValues = {}
        self.resources = {}
        self.microactions = {}
        self.stages = {}
        self.pipelines = {}
        self.corePerfModels = {}
        self.resourceModels = {}
        self.connectorModels = {}

        self.instructions = {}
        self.instructionsGroups = {}

        self.instrMicroactionMapped = []
        self.instrTraceValueMapped = []

        self.ALL_Instruction = MetaModel.Instruction()
        self.ALL_Instruction.name = Defs.KEYWORD_ALL

        self.REST_Instruction = MetaModel.Instruction()
        self.REST_Instruction.name = Defs.KEYWORD_REST

        self.microactionAssignments = {}
        self.resourceAssignments = {}
        
    ## Interface functions
        
    def addConnector(self, name_):
        con = MetaModel.Connector()
        con.name = name_
        self.__addInstance(con, "Connector")

    def addTraceValue(self, name_):
        trVal = MetaModel.TraceValue()
        trVal.name = name_
        self.__addInstance(trVal, "TraceValue")
        
    def addConnectorModel(self, name_, link_, inCons_, outCons_, trVals_):
        conModel = MetaModel.ConnectorModel()
        conModel.name = name_
        conModel.link = link_
        conModel.inConnectors = inCons_
        conModel.outConnectors = outCons_
        conModel.traceValues = trVals_
        self.__addInstance(conModel, "ConnectorModel")

    def addResourceModel(self, name_, link_, trVals_):
        resModel = MetaModel.ResourceModel()
        resModel.name = name_
        resModel.link = link_
        resModel.traceValues = trVals_
        self.__addInstance(resModel, "ResourceModel")

    def addResource(self, name_, delay_=0, model_=None):
        res = MetaModel.Resource()
        res.name = name_
        if((delay_ != 0) and (model_ != None)):
            raise TypeError("Cannot add resource %s with both static (%d) and dynamic (%s) delay" %(name_, delay_, model_.name))
        else:
            res.delay = delay_
            res.resourceModel = model_
        self.__addInstance(res, "Resource")

    def addVirtualResource(self, virAlias_):
        vRes = MetaModel.Resource()
        vRes.virtualAlias = virAlias_
        self.__addInstance(vRes, "Resource")
        
    def addMicroaction(self, name_, refs_):
        uAction = MetaModel.Microaction()
        uAction.name = name_
        
        # Evaluate references (inCon -> Res -> outCon)
        if(len(refs_)>0 and len(refs_)<4):
            nextType = "inCon_or_res"
            for ref in refs_:
                # Input connector
                if((type(ref) is MetaModel.Connector) and nextType == "inCon_or_res"):
                    uAction.inConnector = ref
                    nextType = "res"
                # Resource
                elif((type(ref) is MetaModel.Resource) and (nextType == "inCon_or_res" or nextType == "res")):
                    uAction.resource = ref
                    nextType = "outCon"
                # Output connector
                elif((type(ref) is MetaModel.Connector) and nextType == "outCon"):
                    uAction.outConnector = ref
                    nextType = "none"
                else:
                    print("ERROR: Unexpected reference %s in definition of %s" %(ref.name, name_))
        else:
            raise TypeError("Function addMicroaction for %s called with illegal number of references (%d)" %(name_, len(refs_)))

        self.__addInstance(uAction, "Microaction")

    def addVirtualMicroaction(self, virAlias_):
        vuAction = MetaModel.Microaction()
        vuAction.virtualAlias = virAlias_
        self.__addInstance(vuAction, "Microaction")        
        
    def addStage(self, name_, uActions_):
        stage = MetaModel.Stage()
        stage.name = name_
        stage.microactions = uActions_
        self.__addInstance(stage, "Stage")

    def addPipeline(self, name_, stages_):
        pipe = MetaModel.Pipeline()
        pipe.name = name_
        pipe.stages = stages_
        self.__addInstance(pipe, "Pipeline")

    def addCorePerfModel(self, name_, pipe_, conModels_, resAssigns_, uActionAssigns_):
        model = MetaModel.CorePerfModel()
        model.name = name_
        model.pipeline = pipe_
        model.connectorModels = conModels_
        self.__addInstance(model, "CorePerfModel")
        
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
        instr = MetaModel.Instruction()
        instr.name = name_
        self.__addInstance(instr, "Instruction")

    def mapMicroactions(self, instrOrGroup_, microactions_):
        if type(instrOrGroup_) is InstructionGroup:
            for instr in instrOrGroup_.instructions:
                self.__addMicroactionsToInstruction(instr, microactions_)
        elif type(instrOrGroup_) is MetaModel.Instruction:
            self.__addMicroactionsToInstruction(instrOrGroup_, microactions_)
        else:
            raise TypeError("Function mapMicroactions called with illegal instance of type %s" % type(instrOrGroup_))

    def mapTraceValues(self, instrOrGroup_, traceValMap_):
        if type(instrOrGroup_) is InstructionGroup:
            for instr in instrOrGroup_.instructions:
                self.__addTraceValuesToInstruction(instr, traceValMap_)
        elif type(instrOrGroup_) is MetaModel.Instruction:
            self.__addTraceValuesToInstruction(instrOrGroup_, traceValMap_)
        else:
            raise TypeError("Function mapTraceValues called with illegal instance of type %s" % type(instrOrGroup_))
        
    def getInstance(self, name_, type_):
        subDict = self.__getSubDictionary(type_)
        try:
            inst = subDict[name_]
        except KeyError:
            return UnresolvedReference(name_)
        return subDict[name_]
    
    def isVirtual(self, inst_):

        if not hasattr(inst_, "virtualAlias"):
            return False

        else:
            if inst_.name == "" and inst_.virtualAlias != "":
                return True
            else:
                return False
        
    ## Helper functions

    def __getSubDictionary(self, type_):

        if(type_ == "Connector"):
            return self.connectors
        elif(type_ == "TraceValue"):
            return self.traceValues
        elif(type_ == "ConnectorModel"):
            return self.connectorModels
        elif(type_ == "ResourceModel"):
            return self.resourceModels
        elif(type_ == "Resource"):
            return self.resources
        elif(type_ == "Microaction"):
            return self.microactions
        elif(type_ == "Stage"):
            return self.stages
        elif(type_ == "Pipeline"):
            return self.pipelines
        elif(type_ == "CorePerfModel"):
            return self.corePerfModels
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


    def __addMicroactionsToInstruction(self, instr_, microactions_):
        instr_.microactions.extend(microactions_)
        if (instr_.name != Defs.KEYWORD_ALL) and (instr_.name != Defs.KEYWORD_REST):
            self.instrMicroactionMapped.append(instr_.name)


    def __addTraceValuesToInstruction(self, instr_, traceValueAssigns_):

        for trValAss_i in traceValueAssigns_:
            assignment = MetaModel.TraceValueAssignment()
            assignment.traceValue = trValAss_i[0]
            assignment.description = trValAss_i[1]
            instr_.traceValueAssignments.append(assignment)
        
        #instr_.traceValueAssignments.extend(traceValueAssigns_)
        if (instr_.name != Defs.KEYWORD_ALL) and (instr_.name != Defs.KEYWORD_REST):
            self.instrTraceValueMapped.append(instr_.name)
