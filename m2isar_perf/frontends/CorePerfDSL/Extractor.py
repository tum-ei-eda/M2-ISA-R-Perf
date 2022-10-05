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

from .parser_gen import CorePerfDSLVisitor

from .Dictionary import UnresolvedReference
from . import Defs

class ExtractLevel:

    __BASE_COMPONENTS = 0
    __MODELS_AND_TRACE_VALUE_MAPPING = 1
    __RESOURCES = 2
    __MICROACTIONS = 3
    __STAGES_AND_MICROACTION_MAPPING = 4
    __PIPELINES = 5
    __CORE_PERF_MODEL = 6

    def __init__(self):
        self.__currentLevel = self.__BASE_COMPONENTS

    def getLevel(self):
        return self.__currentLevel

    def increase(self):
        self.__currentLevel += 1

    def isMax(self):
        return (self.__currentLevel == self.__CORE_PERF_MODEL)

    def isLevel(self, name_):
        val = self.__lookupLevelValue(name_)
        return (val == self.__currentLevel)

    def __lookupLevelValue(self, name_):

        if name_ == "BASE_COMPONENTS":
            return self.__BASE_COMPONENTS
        elif name_ == "MODELS_AND_TRACE_VALUE_MAPPING":
            return self.__MODELS_AND_TRACE_VALUE_MAPPING
        elif name_ == "RESOURCES":
            return self.__RESOURCES
        elif name_ == "MICROACTIONS":
            return self.__MICROACTIONS
        elif name_ == "STAGES_AND_MICROACTION_MAPPING":
            return self.__STAGES_AND_MICROACTION_MAPPING
        elif name_ == "PIPELINES":
            return self.__PIPELINES
        elif name_ == "CORE_PERF_MODEL":
            return self.__CORE_PERF_MODEL
    
class Extractor(CorePerfDSLVisitor):
     
    def __init__(self, dict_):
        self.dictionary = dict_
        self.level = ExtractLevel()
        
    def extract(self, tree_):

        while True:
            print("Level: %s" % self.level.getLevel())
            self.visit(tree_)
            if self.level.isMax():
                break
            else:
                self.level.increase()
         
    # Top Node 
    def visitDescription_context(self, ctx):
        self.visitChildren(ctx)
 
    # Level:BASE_COMPONENTS Definitions
   
    def visitConnector(self, ctx):
        if self.level.isLevel("BASE_COMPONENTS"):
            self.dictionary.addConnector(ctx.name.text)

    def visitTraceValue(self, ctx):
        if self.level.isLevel("BASE_COMPONENTS"):
            self.dictionary.addTraceValue(ctx.name.text)
             
    def visitVirtual_def(self, ctx):
        if self.level.isLevel("BASE_COMPONENTS"):
            for v in ctx.virtuals:
                inst_name = v.text
                if ctx.type_.text == "Resource":
                    self.dictionary.addVirtualResource(inst_name)
                elif ctx.type_.text == "Microaction":
                    self.dictionary.addVirtualMicroaction(inst_name)
                else:
                    print("ERROR: Illegal definition of virtual instance %s of type %s" %(inst_name, ctx.type_.text))
              
    def visitInstrGroup(self, ctx):
        if self.level.isLevel("BASE_COMPONENTS"):
            instrs = [instr.text for instr in ctx.instructions]
            self.dictionary.addInstructionGroup(ctx.name.text, instrs)
 
    # Level:MODELS_AND_TRACE_VALUE_MAPPING definitions
 
    def visitConnectorModel(self, ctx):
        if self.level.isLevel("MODELS_AND_TRACE_VALUE_MAPPING"):
            trRefs = [self.visit(tr) for tr in ctx.traceVals]
            inConRefs = [self.visit(inCon) for inCon in ctx.inCons]
            outConRefs = [self.visit(outCon) for outCon in ctx.outCons]
            if ctx.link is not None:
                self.dictionary.addConnectorModel(ctx.name.text, ctx.link.text, inConRefs, outConRefs, trRefs)
            else:
                print("ERROR: ConnectorModel %s defined without a link" % ctx.name.text) # TODO: Add error handling
 
    def visitResourceModel(self, ctx):
        if self.level.isLevel("MODELS_AND_TRACE_VALUE_MAPPING"):
            trRefs = [self.visit(tr) for tr in ctx.traceVals]
            if ctx.link is not None:
                self.dictionary.addResourceModel(ctx.name.text, ctx.link.text, trRefs)
            else:
                print("ERROR: ResourceModel %s defined without a link" % ctx.name.text) # TODO: Add error handling

    def visitTraceValueMapping(self, ctx):
        if self.level.isLevel("MODELS_AND_TRACE_VALUE_MAPPING"):
            instrOrGroup = self.visit(ctx.instr)
            trValAssigns = [self.visit(trVal) for trVal in ctx.trValAssign]
            self.dictionary.mapTraceValues(instrOrGroup, trValAssigns)
            
    # Level:RESOURCES definitions
             
    def visitResource_model(self, ctx):
        if self.level.isLevel("RESOURCES"):
            modelRef = self.visit(ctx.res_model)
            self.dictionary.addResource(ctx.name.text, model_=modelRef)
 
    def visitResource_delay(self, ctx):
        if self.level.isLevel("RESOURCES"):
            self.dictionary.addResource(ctx.name.text, delay_=ctx.delay.text)
             
    def visitResource_default(self, ctx):
        if self.level.isLevel("RESOURCES"):
            self.dictionary.addResource(ctx.name.text, delay_=1)

    # Level:MICROACTIONS definitions

    def visitMicroaction(self, ctx):
        if self.level.isLevel("MICROACTIONS"):
            refs = [self.visit(ref) for ref in ctx.refs]
            self.dictionary.addMicroaction(ctx.name.text, refs)
            
    # Level:STAGES_AND_MICROACTIONS_MAPPING definitions
             
    def visitStage(self, ctx):
        if self.level.isLevel("STAGES_AND_MICROACTION_MAPPING"):
            uARefs = [self.visit(uA) for uA in ctx.microactions]
            self.dictionary.addStage(ctx.name.text, uARefs)

    def visitMicroactionMapping(self, ctx):
        if self.level.isLevel("STAGES_AND_MICROACTION_MAPPING"):
            instrOrGroup = self.visit(ctx.instr)
            uActions = [self.visit(uA) for uA in ctx.microactions]
            self.dictionary.mapMicroactions(instrOrGroup, uActions)

    # Level:PIPELINE definitinons
             
    def visitPipeline(self, ctx):
        if self.level.isLevel("PIPELINES"):
            stRefs = [self.visit(st) for st in ctx.stages]
            self.dictionary.addPipeline(ctx.name.text, stRefs)
 
    # Level:CORE_PERF_MODEL definitinons
             
    def visitCorePerfModel(self, ctx):
        if self.level.isLevel("CORE_PERF_MODEL"):
            conModelRefs = [self.visit(cM) for cM in ctx.conModels]
            resAssigns = [self.visit(resAss) for resAss in ctx.resAssigns]
            uActionAssigns = [self.visit(uAAss) for uAAss in ctx.uActionAssigns]
            
            if ctx.use_pipeline is None:
                print("ERROR: CorePerfModel %s does not specify a pipeline" % ctx.name.text)
            else:
                pipeRef = self.visit(ctx.use_pipeline)
                self.dictionary.addCorePerfModel(ctx.name.text, pipeRef, conModelRefs, resAssigns, uActionAssigns)

                
    # Assignments

    def visitResource_assign(self, ctx):
        v_res = self.visit(ctx.vir_res)
        nv_res = self.visit(ctx.nvir_res)
        if not self.dictionary.isVirtual(v_res):
            print("ERROR: In resource assignment: %s is not a virtual resource" % v_res.name)
        if self.dictionary.isVirtual(nv_res):
            print("ERROR: In resource assignment: %s is a virtual resource" % nv_res.name)
        return (v_res, nv_res)

    def visitMicroaction_assign(self, ctx):
        v_uA = self.visit(ctx.vir_uA)
        nv_uA = self.visit(ctx.nvir_uA)
        if not self.dictionary.isVirtual(v_uA):
            print("ERROR: In microaction assignment: %s is not a virtual microaction" % v_uA.name)
        if self.dictionary.isVirtual(nv_uA):
            print("ERROR: In microaction assignment: %s is a virtual microaction" % nv_uA.name)
        return (v_uA, nv_uA)

    def visitTraceValue_assign(self, ctx):
        trVal = self.visit(ctx.trVal)
        desc = ctx.description.text
        return (trVal, desc)

    # References
                
    def visitConnector_ref(self, ctx):
        return self.__resolveReference(ctx.name.text, "Connector")
        
    def visitTraceValue_ref(self, ctx):
        return self.__resolveReference(ctx.name.text, "TraceValue")
        
    def visitResourceModel_ref(self, ctx):
        return self.__resolveReference(ctx.name.text, "ResourceModel")

    def visitConnectorModel_ref(self, ctx):
        return self.__resolveReference(ctx.name.text, "ConnectorModel")
    
    def visitResource_ref(self, ctx):
        return self.__resolveReference(ctx.name.text, "Resource")
    
    def visitResourceOrConnector_ref(self, ctx):
        ref = self.dictionary.getInstance(ctx.name.text, "Resource")
        if type(ref) is UnresolvedReference:
            ref = self.dictionary.getInstance(ctx.name.text, "Connector")
            if type(ref) is UnresolvedReference:
                print("ERROR: Could not resolve reference %s. Neiter a resource nor a connector instance." % ctx.name.text)
        return ref

    def visitMicroaction_ref(self, ctx):
        return self.__resolveReference(ctx.name.text, "Microaction")

    def visitStage_ref(self, ctx):
        return self.__resolveReference(ctx.name.text, "Stage")

    def visitPipeline_ref(self, ctx):
        return self.__resolveReference(ctx.name.text, "Pipeline")

    def visitInstructionOrInstrGroup_ref(self, ctx):
        if(ctx.name.text == Defs.KEYWORD_ALL):
            ref = self.dictionary.ALL_Instruction
        elif(ctx.name.text == Defs.KEYWORD_REST):
            ref = self.dictionary.REST_Instruction
        else:
            ref = self.dictionary.getInstance(ctx.name.text, "InstructionGroup")
            if type(ref) is UnresolvedReference:
                ref = self.dictionary.getInstance(ctx.name.text, "Instruction")
                if type(ref) is UnresolvedReference:
                    self.dictionary.addInstruction(ctx.name.text)
                    ref = self.dictionary.getInstance(ctx.name.text, "Instruction")
        return ref
    
    # Helper functions

    def __resolveReference(self, name_, type_):
        ref = self.dictionary.getInstance(name_, type_)
        if type(ref) is UnresolvedReference:
            print("ERROR: Could not resolve reference %s of type %s. No such instance." %(name_, type_))
        return ref
