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

import Instances as inst

class Description:

    def __init__(self):
        self.instructionList = inst.InstanceList()
        self.connectorList = inst.InstanceList()
        self.traceValueList = inst.InstanceList()
        self.instrGroupList = inst.InstanceList()
        self.resourceModelList = inst.InstanceList()
        self.connectorModelList = inst.InstanceList()
        self.resourceList = inst.InstanceList()
        self.microactionList = inst.InstanceList()
        self.stageList = inst.InstanceList()
        self.microactionMappingList = inst.InstanceList()
        self.pipelineList = inst.InstanceList()
        self.corePerfModelList = inst.InstanceList()
        
    def addInstruction(self, name_):
        instr = inst.InstructionInstance(name_)
        self.instructionList.add(instr)

    def addConnector(self, name_):
        con = inst.ConnectorInstance(name_)
        self.connectorList.add(con)

    def addTraceValue(self, name_):
        tr = inst.TraceValueInstance(name_)
        self.traceValueList.add(tr)

    def addVirtual(self, name_, type_):
        if(type_ == "Resource"):
            vres = inst.ResourceInstance(name_, True)
            self.resourceList.add(vres)
        elif(type_ == "Microaction"):
            vuA = inst.MicroactionInstance(name_, True)
            self.microactionList.add(vuA)

    def addInstrGroup(self, name_, instructions_):
        gr = inst.InstrGroupInstance(name_)
        gr.instructions = instructions_
        self.instrGroupList.add(gr)

    def addResourceModel(self, name_, link_, trRefs_):
        rM = inst.ResourceModelInstance(name_)
        rM.link = link_
        rM.traceVals = trRefs_
        self.resourceModelList.add(rM)

    def addConnectorModel(self, name_, link_, trRefs_, inConRefs_, outConRefs_):
        cM = inst.ConnectorModelInstance(name_)
        cM.link = link_
        cM.traceVals = trRefs_
        cM.inCons = inConRefs_
        cM.outCons = outConRefs_
        self.connectorModelList.add(cM)
        
    def addResource(self, name_, dyn_delay_, model_or_delay_):
        res = inst.ResourceInstance(name_)
        res.dynamic_delay = dyn_delay_
        if(dyn_delay_):
            res.model = model_or_delay_
        else:
            res.delay = int(model_or_delay_)
        self.resourceList.add(res)

    def addMicroaction(self, name_, *args):
        uA = inst.MicroactionInstance(name_)

        if(len(args) == 3):
            uA.inConnector = args[0]
            uA.resource = args[1]
            uA.outConnector = args[2]

        elif(len(args) == 2):
            if type(args[0]) is inst.ConnectorInstance:
                uA.inConnector = args[0]
                if type(args[1]) is inst.ResourceInstance:
                    uA.resource = args[1]
                else:
                    print("ERROR: Definition of microaction %s. Unexpected argument %s. Expected a reference to a resource." % (uA.name, args[1].name))

            elif type(args[0]) is inst.ResourceInstance:
                uA.resource = args[0]
                if type(args[1]) is inst.ConnectorInstance:
                    uA.outConnector = args[1]
                else:
                    print("ERROR: Definition of microaction %s. Unexpected argument %s. Expected a reference to a connector." % (uA.name, args[1].name))
            else:
                print("ERROR: Definition of microaction %s. Unexpected argument %s. Expected a reference to a connector or to a resource." % (uA.name, args[0].name))
                    
        elif(len(args) == 1):
            if type(args[0]) is inst.ConnectorInstance:
                uA.inConnector = args[0]
            elif type(args[0]) is inst.ResourceInstance:
                uA.resource = args[0]
            else:
                print("ERROR: Definition of microaction %s. Unexpected argument %s. Expected a reference to a connector or to a resource." % (uA.name, args[0].name))

        self.microactionList.add(uA)

    def addStage(self, name_, microactions_):
        st = inst.StageInstance(name_)
        st.microactions = microactions_
        self.stageList.add(st)

    def addMicroactionMapping(self, instr_or_group_, microactions_):
        map = inst.MicroactionMappingInstance("MicroactionMapping_" + instr_or_group_.name)
        if type(instr_or_group_) is inst.InstructionInstance:
            map.singleInstr = True
            map.instr = instr_or_group_
        else:
            map.singleInstr = False
            map.instrGr = instr_or_group_
        map.microactions = microactions_
        self.microactionMappingList.add(map)
        
    def addPipeline(self, name_, stages_):
        pipe = inst.PipelineInstance(name_)
        pipe.stages = stages_
        self.pipelineList.add(pipe)

    def addCorePerfModel(self, name_, pipeline_, conModels_, vir_Res_, nvir_Res_, vir_uA_, nvir_uA_):
        model = inst.CorePerfModelInstance(name_)
        model.pipeline = pipeline_
        model.connectorModels = conModels_
        for (vR, R) in zip(vir_Res_, nvir_Res_):
            model.resourceAssignments.append((vR, R))
        for (vuA, uA) in zip(vir_uA_, nvir_uA_):
            model.microactionAssignments.append((vuA, uA))
        self.corePerfModelList.add(model)
