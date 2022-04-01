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

from parser_gen import CorePerfDSLVisitor

from Description import Description
from Instances import UndefinedInstance

class Extractor():

    def __init__(self):
        self.description = Description()

    def extract(self, tree):
        visitor = ExtractVisitor(self.description)

        while True:
            print("Level: %s" % visitor.getLevel())
            visitor.visit(tree)
            if visitor.reachedMaxLevel():
                break
            else:
                visitor.nextLevel()

        return self.description
        
class ExtractVisitor(CorePerfDSLVisitor):

    def __init__(self, description_):
        self.level = 0
        self.description = description_
        self.MAX_LEVEL = 6
        
    # Top Node

    def visitDescription_context(self, ctx):
        self.visitChildren(ctx)

    # Level 0 Definitions
    
    def visitConnector(self, ctx):
        if self.level == 0:
            self.description.addConnector(ctx.name.text)

    def visitTraceValue(self, ctx):
        if self.level == 0:
            self.description.addTraceValue(ctx.name.text)
            
    def visitVirtual_def(self, ctx):
        if self.level == 0:
            for v in ctx.virtuals:
                inst_name = self.visit(v)
                self.description.addVirtual(inst_name, ctx.type_.text)

    def visitVirtual(self, ctx):
        return ctx.name.text
            
    def visitInstrGroup(self, ctx):
        if self.level == 0:
            instructions = [self.visit(inst) for inst in ctx.instructions] # TODO: Make instr.Instance? Rather than string handling?
            self.description.addInstrGroup(ctx.name.text, instructions)

    # Level 1 definitions

    def visitConnectorModel(self, ctx):
        if self.level == 1:
            trRefs = [self.visit(tr) for tr in ctx.traceVals]
            inConRefs = [self.visit(inCon) for inCon in ctx.inCons]
            outConRefs = [self.visit(outCon) for outCon in ctx.outCons]
            if ctx.link is not None:
                self.description.addConnectorModel(ctx.name.text, ctx.link.text, trRefs, inConRefs, outConRefs)
            else:
                print("ERROR: ResourceModel %s defined without a link" % ctx.name.text)

    def visitResourceModel(self, ctx):
        if self.level == 1:
            trRefs = [self.visit(tr) for tr in ctx.traceVals]
            if ctx.link is not None:
                self.description.addResourceModel(ctx.name.text, ctx.link.text, trRefs)
            else:
                print("ERROR: ResourceModel %s defined without a link" % ctx.name.text)
        
    # Level 2 definitions
            
    def visitResource_model(self, ctx):
        if self.level == 2:
            modelRef = self.visit(ctx.res_model)
            self.description.addResource(ctx.name.text, True, modelRef)

    def visitResource_delay(self, ctx):
        if self.level == 2:
            self.description.addResource(ctx.name.text, False, ctx.delay.text)
            
    def visitResource_default(self, ctx):
        if self.level == 2:
             self.description.addResource(ctx.name.text, False, "1")

    # Level 3 definitions
            
    def visitMicroaction_single_arg(self, ctx):
        if self.level == 3:
            ref_1 = self.visit(ctx.ref_1)
            self.description.addMicroaction(ctx.name.text, ref_1)

    def visitMicroaction_double_arg(self, ctx):
        if self.level == 3:
            ref_1 = self.visit(ctx.ref_1)
            ref_2 = self.visit(ctx.ref_2)
            self.description.addMicroaction(ctx.name.text, ref_1, ref_2)

    def visitMicroaction_triple_arg(self, ctx):
        if self.level == 3:
            ref_1 = self.visit(ctx.ref_1)
            ref_2 = self.visit(ctx.ref_2)
            ref_3 = self.visit(ctx.ref_3)
            self.description.addMicroaction(ctx.name.text, ref_1, ref_2, ref_3)
            
    # Level 4 definitions
            
    def visitStage(self, ctx):
        if self.level == 4:
            uARefs = [self.visit(uA) for uA in ctx.microactions]
            self.description.addStage(ctx.name.text, uARefs)

    def visitMicroactionMapping(self, ctx):
        if self.level == 4:
            instrRef = self.visit(ctx.instr)
            uARefs = [self.visit(uA) for uA in ctx.microactions]
            self.description.addMicroactionMapping(instrRef, uARefs)
            
    # Level 5 definitinons
            
    def visitPipeline(self, ctx):
        if self.level == 5:
            stRefs = [self.visit(st) for st in ctx.stages]
            self.description.addPipeline(ctx.name.text, stRefs)

    # Level 6 definitinons
            
    def visitCorePerfModel(self, ctx):
        if self.level == 6:
            conModelRefs = [self.visit(cM) for cM in ctx.conModels]
            vir_ResRefs = [self.visit(res) for res in ctx.vir_Res]
            nvir_ResRefs = [self.visit(res) for res in ctx.nvir_Res]
            vir_uARefs = [self.visit(uA) for uA in ctx.vir_uA]
            nvir_uARefs = [self.visit(uA) for uA in ctx.nvir_uA]
            if ctx.use_pipeline is None:
                print("ERROR: CorePerfModel %s does not specify a pipeline" % ctx.name.text)
            else:
                pipeRef = self.visit(ctx.use_pipeline)
                self.description.addCorePerfModel(ctx.name.text, pipeRef, conModelRefs, vir_ResRefs, nvir_ResRefs, vir_uARefs, nvir_uARefs)
            

    # References

    def visitInstruction_ref(self, ctx):
        return self.getOrCreateInstruction(ctx)

    def visitConnector_ref(self, ctx):
        return self.checkReference(ctx, "Connector")
    
    def visitTraceValue_ref(self, ctx):
        return self.checkReference(ctx, "TraceValue")

    def visitResourceModel_ref(self, ctx):
        return self.checkReference(ctx, "ResourceModel")

    def visitConnectorModel_ref(self, ctx):
        return self.checkReference(ctx, "ConnectorModel")
    
    def visitResource_ref(self, ctx):
        return self.checkReference(ctx, "Resource")

    def visitVirResource_ref(self, ctx):
        return self.checkVirtualReference(ctx, "Resource")
        
    def visitNonVirResource_ref(self, ctx):
        return self.checkNonVirtualReference(ctx, "Resource")
        
    def visitResourceOrConnector_ref(self, ctx):
        ref = self.checkReference(ctx, "Resource", True)
        if type(ref) is UndefinedInstance:
            ref = self.checkReference(ctx, "Connector", True)
            if type(ref) is UndefinedInstance:
                print("ERROR: Reference %s does neither name an existing Resource nor Connector" % ctx.name.text)
                return UndefinedInstance(ctx.name.text)
        return ref

    def visitMicroaction_ref(self, ctx):
        return self.checkReference(ctx, "Microaction")

    def visitVirMicroaction_ref(self, ctx):
        return self.checkVirtualReference(ctx, "Microaction")

    def visitNonVirMicroaction_ref(self, ctx):
        return self.checkNonVirtualReference(ctx, "Microaction")
    
    def visitInstructionOrInstrGroup_ref(self, ctx):
        ref = self.checkReference(ctx, "InstrGroup", True)
        if type(ref) is UndefinedInstance:
            ref = self.getOrCreateInstruction(ctx)
        return ref

    def visitStage_ref(self, ctx):
        return self.checkReference(ctx, "Stage")

    def visitPipeline_ref(self, ctx):
        return self.checkReference(ctx, "Pipeline")
    
    # Helper Functions

    def checkReference(self, ctx, type_str, suppress_error=False):

        if (type_str == "Instruction"):
            list = self.description.instructionList
        elif (type_str == "Connector"):
            list = self.description.connectorList
        elif(type_str == "TraceValue"):
            list = self.description.traceValueList
        elif(type_str == "ResourceModel"):
            list = self.description.resourceModelList
        elif(type_str == "ConnectorModel"):
            list = self.description.connectorModelList
        elif(type_str == "Resource"):
            list = self.description.resourceList
        elif(type_str == "Microaction"):
            list = self.description.microactionList
        elif(type_str == "InstrGroup"):
            list = self.description.instrGroupList
        elif(type_str == "Stage"):
            list = self.description.stageList
        elif(type_str == "Pipeline"):
            list = self.description.pipelineList
            
        if list.exists(ctx.name.text):
            return list.get(ctx.name.text)
        else:
            if not suppress_error:
                print("ERROR: Reference %s does not name an existing %s" % (ctx.name.text, type_str))
            return UndefinedInstance(ctx.name.text)

    def checkVirtualReference(self, ctx, type_str):
        ref = self.checkReference(ctx, type_str)
        if ref.isVirtual():
            return ref
        print("ERROR: Reference %s does not name an existing virtual %s" % (ctx.name.text, type_str))
        return UndefinedInstance(ctx.name.text)

    def checkNonVirtualReference(self, ctx, type_str):
        ref = self.checkReference(ctx, type_str)
        if not ref.isVirtual():
            return ref
        print("ERROR: Reference %s does not name an existing virtual %s" % (ctx.name.text, type_str))
        return UndefinedInstance(ctx.name.text)
        
    def getOrCreateInstruction(self, ctx):
        ref = self.checkReference(ctx, "Instruction", True)
        if type(ref) is not UndefinedInstance:
            return ref
        else:
            self.description.addInstruction(ctx.name.text)
            return self.description.instructionList.get(ctx.name.text)
        
    def nextLevel(self):
        self.level += 1

    def getLevel(self):
        return self.level
        
    def reachedMaxLevel(self):
        return self.level == self.MAX_LEVEL
