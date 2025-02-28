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

        # Iterate over tree
        while True:
            self.visit(tree_)
            if self.level.isMax():
                break
            else:
                self.level.increase()

        # Establish previously unresolved references
        # NOTE: Currently, this is only done for stages, as stages and pipelines can reference each other.
        # TODO: Consider doing this for each type? This would allow to stop iterating through the tree based on levels.
        self.dictionary.resolveStages()
                
    # Top Node 
    def visitTop(self, ctx):
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

    def visitResource(self, ctx):
        if self.level.isLevel("RESOURCES"):

            # Check for delay
            delay = 1
            dynDelay = False
            if ctx.delay: # Static delay
                delay = int(ctx.delay.text)
            elif ctx.res_model: # Dynamic delay (external resource model)
                delay = self.visit(ctx.res_model)
                dynDelay = True

            # Add resource
            if dynDelay:
                self.dictionary.addResource(ctx.name.text, model_=delay)
            else:
                self.dictionary.addResource(ctx.name.text, delay_=delay)
    
    # def visitResource_model(self, ctx):
    #     if self.level.isLevel("RESOURCES"):
    #         modelRef = self.visit(ctx.res_model)
    #         self.dictionary.addResource(ctx.name.text, model_=modelRef)
    # 
    # def visitResource_delay(self, ctx):
    #     if self.level.isLevel("RESOURCES"):
    #         self.dictionary.addResource(ctx.name.text, delay_=ctx.delay.text)
    #          
    # def visitResource_default(self, ctx):
    #     if self.level.isLevel("RESOURCES"):
    #         self.dictionary.addResource(ctx.name.text, delay_=1)

    # Level:MICROACTIONS definitions

    def visitMicroaction(self, ctx):
        if self.level.isLevel("MICROACTIONS"):
            refs = []
            refs.append(self.visit(ctx.comps_1))
            if ctx.comps_2:
                refs.append(self.visit(ctx.comps_2))
            if ctx.comps_3:
                refs.append(self.visit(ctx.comps_3))
            self.dictionary.addMicroaction(ctx.name.text, refs)    
                
    def visitMicroactionComponent(self, ctx):
        if self.level.isLevel("MICROACTIONS"):
            if ctx.singleComponent:
                return [self.visit(ctx.singleComponent)]
            elif ctx.multipleComponents:
                return self.visit(ctx.multipleComponents)

    def visitMicroactionComponent_list(self, ctx):
        if self.level.isLevel("MICROACTIONS"):
            refs = [self.visit(ref) for ref in ctx.refs]
            refType = type(refs[0])
            for ref_i in refs:
                if type(ref_i) is not refType:
                    print(f"ERROR [Line {ctx.start.line}]: Set of Microaction-components of different types") # TODO: Unify error handling
        return refs
                
    # Level:STAGES_AND_MICROACTIONS_MAPPING definitions
             
    def visitStage(self, ctx):
        if self.level.isLevel("STAGES_AND_MICROACTION_MAPPING"):

            # Check for attributes
            capacity = 1
            hasOutputBuffer = False
            if ctx.attributes:
                for attr_i in ctx.attributes:
                    if attr_i.capacity:
                        capacity = int(attr_i.capacity.text)
                    if attr_i.getText() == "output-buffer":
                        hasOutputBuffer = True

            pathRefs = [self.visit(p) for p in ctx.paths] # microaction or pipeline refs
            self.dictionary.addStage(ctx.name.text, pathRefs, capacity, hasOutputBuffer)

    def visitMicroactionMapping(self, ctx):
        if self.level.isLevel("STAGES_AND_MICROACTION_MAPPING"):
            instrOrGroup = self.visit(ctx.instr)
            uActions = [self.visit(uA) for uA in ctx.microactions]
            self.dictionary.mapMicroactions(instrOrGroup, uActions)

    # Level:PIPELINE definitinons
             
    def visitPipeline(self, ctx):
        if self.level.isLevel("PIPELINES"):
            
            # Check for attributes
            if ctx.attribute:
                blockPipelineRefs = [self.visit(pipe) for pipe in ctx.attribute.blockPipelines]
            else:
                blockPipelineRefs = []
                
            # Read components
            isParallel = False
            if ctx.sequentialComponentList:
                compRefs = self.visit(ctx.sequentialComponentList)
            elif ctx.parallelComponentList:
                isParallel = True
                compRefs = self.visit(ctx.parallelComponentList)
                
            self.dictionary.addPipeline(ctx.name.text, compRefs, isParallel, blockPipelineRefs)

    def visitPipeline_sequential(self, ctx):
        if self.level.isLevel("PIPELINES"):
            return [self.visit(comp) for comp in ctx.components]

    def visitPipeline_parallel(self, ctx):
        if self.level.isLevel("PIPELINES"):
            return [self.visit(comp) for comp in ctx.components]
            
    # Level:CORE_PERF_MODEL definitinons
             
    def visitCorePerfModel(self, ctx):
        if self.level.isLevel("CORE_PERF_MODEL"):
            conModelRefs = [self.visit(cM) for cM in ctx.conModels]
            resAssigns = [self.visit(resAss) for resAss in ctx.resAssigns]
            uActionAssigns = [self.visit(uAAss) for uAAss in ctx.uActionAssigns]
            
            #if ctx.use_pipeline is None:
            #    print("ERROR: CorePerfModel %s does not specify a pipeline" % ctx.name.text)
            #else:
            #    pipeRef = self.visit(ctx.use_pipeline)
            #    self.dictionary.addCorePerfModel(ctx.name.text, pipeRef, conModelRefs, resAssigns, uActionAssigns)

            # Check that required arguments are present
            if ctx.use_pipeline is None:
                raise RuntimeError(f"CorePerfModel {ctx.name.text} does not specify a pipeline [Line: {ctx.start.line}]") # TODO: Unify error handling
            pipeRef = self.visit(ctx.use_pipeline)

            if ctx.core is None:
                raise RuntimeError(f"CorePerfModel {ctx.name.text} does not specify a core [Line: {ctx.start.line}]") # TODO: Unify error handling

            # Add model to dictionary
            self.dictionary.addVariant(ctx.name.text, pipeRef, ctx.core.text, conModelRefs, resAssigns, uActionAssigns)
            
                
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
        desc = self.__processStrObj(ctx.description.text)
        return (trVal, desc)

    # References
                
    def visitConnector_ref(self, ctx):
        return self.__resolveReference(ctx.name.text, "Connector", ctx.start.line)
        
    def visitTraceValue_ref(self, ctx):
        return self.__resolveReference(ctx.name.text, "TraceValue", ctx.start.line)
        
    def visitResourceModel_ref(self, ctx):
        return self.__resolveReference(ctx.name.text, "ResourceModel", ctx.start.line)

    def visitConnectorModel_ref(self, ctx):
        return self.__resolveReference(ctx.name.text, "ConnectorModel", ctx.start.line)
    
    def visitResource_ref(self, ctx):
        return self.__resolveReference(ctx.name.text, "Resource", ctx.start.line)
    
    def visitResourceOrConnector_ref(self, ctx):
        ref = self.dictionary.getInstance(ctx.name.text, "Resource", ctx.start.line)
        if type(ref) is UnresolvedReference:
            ref = self.dictionary.getInstance(ctx.name.text, "Connector", ctx.start.line)
            if type(ref) is UnresolvedReference:
                ref.reportError()
        return ref

    def visitMicroaction_ref(self, ctx):
        return self.__resolveReference(ctx.name.text, "Microaction", ctx.start.line)

    def visitStage_ref(self, ctx):
        return self.__resolveReference(ctx.name.text, "Stage", ctx.start.line)
        
    def visitPipeline_ref(self, ctx):
        return self.__resolveReference(ctx.name.text, "Pipeline", ctx.start.line)

    def visitInstructionOrInstrGroup_ref(self, ctx):
        if(ctx.name.text == Defs.KEYWORD_ALL):
            ref = self.dictionary.ALL_Instruction
        elif(ctx.name.text == Defs.KEYWORD_REST):
            ref = self.dictionary.REST_Instruction
        else:
            ref = self.dictionary.getInstance(ctx.name.text, "InstructionGroup", ctx.start.line)
            if type(ref) is UnresolvedReference:
                ref = self.dictionary.getInstance(ctx.name.text, "Instruction", ctx.start.line)
                if type(ref) is UnresolvedReference:
                    self.dictionary.addInstruction(ctx.name.text)
                    ref = self.dictionary.getInstance(ctx.name.text, "Instruction", ctx.start.line)
        return ref

    def visitMicroactionOrPipeline_ref(self, ctx):
        ref = self.dictionary.getInstance(ctx.name.text, "Microaction", ctx.start.line)
        if type(ref) is UnresolvedReference:
            ref = self.dictionary.getInstance(ctx.name.text, "Pipeline", ctx.start.line) # Will try to resolve this again after tree is read in -> no error
        return ref

    def visitStageOrPipeline_ref(self, ctx):
        ref = self.dictionary.getInstance(ctx.name.text, "Stage", ctx.start.line)
        if type(ref) is UnresolvedReference:
            ref = self.__resolveReference(ctx.name.text, "Pipeline", ctx.start.line)
        return ref
            
    # Helper functions

    def __resolveReference(self, name_, type_, line_=0):
        ref = self.dictionary.getInstance(name_, type_, line_)
        if type(ref) is UnresolvedReference:
            ref.reportError()
        return ref

    # NOTE: Current CorePerfDSL.g4 setup causes string to be read including quotes (").
    #       Removing quotes here to be alligned with other reads
    #       Might be able to do this directly in CorePerfDSL.g4 with action for Lexer rule STRING,
    #       but so far could not figure out how to do this with created python-Lexer
    def __processStrObj(self, str_):
        ret_str = str_[1:len(str_)-1] # Remove start and end quote
        ret_str = ret_str.replace('\\"', "\"")
        return ret_str
