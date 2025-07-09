# 
# Copyright 2025 Chair of EDA, Technical University of Munich
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

from meta_models.structural_model.StructuralModel import Microaction

class CorePerfDslBuilder:

    def __init__(self):
        pass

    def getMicroactionDef(self, uAction_):
        retStr = "( "
        inCons = uAction_.getInConnectors()
        res = uAction_.getResources()
        outCons = uAction_.getOutConnectors()
        
        hasInCons = False
        if inCons:
            hasInCons = True
            if len(inCons) == 1:
                retStr += inCons[0].name
            else:
                retStr += "{ "
                for i, iC_i in enumerate(inCons):
                    retStr += (iC_i.name + ", ") if i < len(inCons)-1 else iC_i.name
                retStr += " }"

        hasResources = False
        if res:
            hasResources = True
            if hasInCons:
                retStr += " -> "
            if len(res) == 1:
                retStr += self.__getResourceRef(res[0])
            else:
                retStr += "{ "
                for i, res_i in enumerate(res):
                    resName = self.__getResourceRef(res_i)
                    retStr += (resName + ", ") if i < len(res)-1 else resName
                retStr += " }"

        if outCons:
            if hasResources:
                retStr += " -> "
                if len(outCons) == 1:
                    retStr += outCons[0].name
                else:
                    retStr += "{ "
                    for i, oC_i in enumerate(outCons):
                        retStr += (oC_i.name + ", ") if i < len(outCons)-1 else oC_i.name
                    retStr += " }"

        retStr += " )"
        return retStr

    def getResourceDef(self, res_):
        if res_.hasDynamicDelay():
            return "(" + res_.getResourceModelName() + ")"
        elif res_.delay > 1:
                return "(" + str(res_.delay) + ")"
        return ""

    def getStageDef(self, st_):
        retStr = "( "
        paths = st_.getPaths()
        for i, path_i in enumerate(paths):
            pathName = path_i.name
            if type(path_i) is Microaction:
                if path_i.isVirtual():
                    pathName = path_i.getVirtualAlias()
            retStr += (pathName + ", ") if i < len(paths)-1 else pathName
        retStr += " )"
        return retStr

    def getPipelineDef(self, pipe_):
        retStr = "( "
        comps = pipe_.getComponents()
        connector = "|" if pipe_.isParallel else "->"
        for i, comp_i in enumerate(comps):
            retStr += (comp_i.name + connector + " ") if i <len(comps)-1 else comp_i.name
        retStr += " )"
        return retStr

    def getModelAttr(self, model_):
        retStr = ""
        setComma = False
        if model_.isConfig or model_.hasInfoTrace:
            retStr += "[ "
            if model_.isConfig:
                retStr += "config"
                setComma = True
            if model_.hasInfoTrace:
                if setComma:
                    retStr += " , "
                retStr += "info-trace"
            retStr += " ]"
        return retStr

    def getModelDef(self, model_):
        retStr = "(\n"
        retStr += "\tlink : \"" + model_.link + "\"\n"

        trVals = model_.getTraceValues()
        if trVals:
            retStr += "\ttrace : { "
            for i, trVal_i in enumerate(trVals):
                retStr += (trVal_i.name + ", ") if i < len(trVals)-1 else trVal_i.name
            retStr += " }\n"

        inCons = model_.getInConnectors()
        if inCons:
            retStr += "\tconnectorIn : { "
            for i, con_i in enumerate(inCons):
                retStr += (con_i.name + ", ") if i < len(inCons)-1 else con_i.name
            retStr += " }\n"

        outCons = model_.getOutConnectors()
        if outCons:
            retStr += "\tconnectorOut : { "
            for i, con_i in enumerate(outCons):
                retStr += (con_i.name + ", ") if i < len(outCons)-1 else con_i.name
            retStr += " }\n"

        retStr += ")"
        return retStr

    def getInstrName(self, instr_):
        if instr_.name == "_def":
            return "Default"
        return instr_.name

    def getMicroactionMapping(self, uActionList_):
        retStr = "{ "
        for i, uA_i in enumerate(uActionList_):
            retStr += (uA_i.name + ", ") if i < len(uActionList_)-1 else uA_i.name
        retStr += " }"
        return retStr

    def getTraceValueMapping(self, instr_):
        retStr = "{\n"
        trValAssignments = instr_.getTraceValueAssignments()
        for i, trValAss_i in enumerate(trValAssignments):
            retStr += "\t" + trValAss_i.getTraceValue().name + " = \"" + trValAss_i.getDescription() + "\""
            retStr += ",\n" if i < len(trValAssignments)-1 else "\n"
        retStr += "}"
        return retStr

    def getVariantDef(self, var_):
        retStr = "(\n"
        retStr += "\tuse Pipeline : " + var_.getPipeline().name + "\n"

        conModels = [i for i in var_.getAllModels() if i.isConnectorModel]
        if conModels:
            retStr += "\tuse ConnectorModel : {\n"
            for i, mod_i in enumerate(conModels):
                retStr += "\t\t" + mod_i.name
                retStr += ",\n" if i < len(conModels)-1 else "\n"
            retStr += "\t}\n"

        virMicroactions = [i for i in var_.getAllMicroactions() if i.isVirtual()]
        if virMicroactions:
            retStr += "\tassign Microaction : {\n"
            for i, uA_i in enumerate(virMicroactions):
                retStr += "\t\t" + uA_i.virtualAlias + " = " + uA_i.name
                retStr += ",\n" if i < len(virMicroactions)-1 else "\n"
            retStr += "\t}\n"

        virResources = [i for i in var_.getAllResources() if i.isVirtual()]
        if virResources:
            retStr += "\tassign Resource : {\n"
            for i, res_i in enumerate(virResources):
                retStr += "\t\t" + res_i.virtualAlias + " = " + res_i.name
                retStr += ",\n" if i < len(virResources)-1 else "\n"
            retStr += "\t}\n"

        retStr += ")"
        return retStr
            

    def __getResourceRef(self, res_):
        if res_.isVirtual():
            return res_.getVirtualAlias()
        return res_.name
