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

import pathlib
import shutil
import os

from mako.template import Template

from . import Defs

class ModelPrinter:

    def __init__(self, tempDir_, templateDir_, outDir_):
        self.tempDirBase = tempDir_ / "model"
        self.templateDir = templateDir_ / "model"
        self.outDirBase = outDir_

    def printModel(self, model_):

        for cPM in model_.getAllCorePerfModels():
            self.__printCorePerfModel(cPM)
        
    def __printCorePerfModel(self, corePerfModel_):
        
        self.corePerfModel = corePerfModel_

        self.curTempDir = self.tempDirBase / self.corePerfModel.name
        self.curOutDir = self.outDirBase / self.corePerfModel.name
        
        self.totalNumConModels = 0
        self.totalNumStages = 0
        self.totalNumConLinks = 0
        self.maxNumMicroactions = 0

        print("")
        print("Creating model diagrams for %s" %self.corePerfModel.name)
        
        self.__createMicroactions()
        self.__createConnectorModels()
        self.__createStages()
        self.__createSizeConfig()
        self.__createCore()

        self.__makeOverviewPdf()
        for instr in self.corePerfModel.getAllInstructions():
            self.__makeInstructionPdf(instr)
        
    ## Sub-Functions
        
    def __createMicroactions(self):
        tempDir_uA = self.__createSubDir_temp("microactions")

        for uA in self.corePerfModel.getAllMicroactions():

            renderDict = {"microaction": uA}
            
            self.__renderAndCreate("microaction", renderDict, tempDir_uA / (uA.name + ".tex"))
            
    def __createConnectorModels(self):
        tempDir_conMod = self.__createSubDir_temp("connectorModels")
        
        for conMod in self.corePerfModel.getAllConnectorModels():
            self.totalNumConModels += 1

            # Find number of inputs (outConnectors) and outputs (inConnectors) connected to this model
            numInputs = 0
            numOutputs = 0
            for uA in self.corePerfModel.getAllMicroactions():

                inCon = uA.getInConnector()
                if (inCon is not None) and (inCon.getConnectorModel() is conMod):
                    numOutputs += 1

                outCon = uA.getOutConnector()
                if (outCon is not None) and (outCon.getConnectorModel() is conMod):
                    numInputs += 1

            # Render and create file
            renderDict = {"connectorModel": conMod,
                          "numInputs": numInputs,
                          "numOutputs": numOutputs}

            self.__renderAndCreate("connectorModel", renderDict, tempDir_conMod / (conMod.name + ".tex"))

    def __createStages(self):
        tempDir_st = self.__createSubDir_temp("stages")

        numPrevOutCons = 0
        drawnConModList = []

        for st in self.corePerfModel.getAllStages():
            self.totalNumStages += 1

            numMicroactions = 0
            numInCons = 0
            numOutCons = 0
            conModList = []

            # Count used microactions. Count in and output connectors for the stage
            # Establish if a conModel should be drawn below the stage (model connected to inConnector and has not been drawn before)
            for uA in st.getUsedMicroactions():
                numMicroactions += 1

                if (uA.getOutConnector() is not None):
                    numOutCons += 1

                inCon = uA.getInConnector()
                if (inCon is not None):
                    numInCons += 1
                    conMod = inCon.getConnectorModel()
                    if conMod not in drawnConModList:
                        conModList.append(conMod)
                        drawnConModList.append(conMod)

            if numMicroactions > self.maxNumMicroactions:
                self.maxNumMicroactions = numMicroactions

            self.totalNumConLinks += (numInCons + numOutCons)

            numConLinks = numInCons + numPrevOutCons
            numPrevOutCons = numOutCons

            # Render and create file
            renderDict = {"stage": st,
                          "numConnectorLinks" : numConLinks,
                          "connectorModelList" : conModList}

            self.__renderAndCreate("stage", renderDict, tempDir_st / (st.name + ".tex"))

    def __createSizeConfig(self):
        renderDict = {"maxNumMicroactions": self.maxNumMicroactions,
                      "numConnectorLinks": self.totalNumConLinks,
                      "numStages": self.totalNumStages,
                      "numConnectorModels": self.totalNumConModels}

        self.__renderAndCreate("size_config", renderDict, self.curTempDir / "size_config.tex")

    def __createCore(self):
        renderDict = {"corePerfModel": self.corePerfModel}
        self.__renderAndCreate("core", renderDict, self.curTempDir / "core.tex")

    def __makeOverviewPdf(self):
        self.__makePdf(Defs.OVERVIEW_FOLDER, [])

    def __makeInstructionPdf(self, instr_):
        self.__makePdf(instr_.name, instr_.getUsedMicroactions())
        
    ## Helper Functions

    def __createSubDir_temp(self, name_):
        subDir = self.curTempDir / name_
        pathlib.Path(subDir).mkdir(parents=True)
        return subDir

    def __getSubDir_out(self, name_):
        return self.curOutDir / name_
    
    def __renderAndCreate(self, template_, renderDict_, file_):

        template = Template(filename = str(self.templateDir) + "/" + template_ + ".mako")
        latex = template.render(**renderDict_)

        with file_.open('w') as f:
            f.write(latex)
    
    def __makePdf(self, name_, usedMicroactions_):

        print("\tMaking PDF for %s" %name_)

        tempDir_model = self.__createSubDir_temp(name_)
                
        # Copy main file macro (does not require rendering)
        renderDict = {"name": name_}
        self.__renderAndCreate("main", renderDict, tempDir_model / (name_ + ".tex"))

        # Create and render use_config file
        renderDict = {"microactionList": self.corePerfModel.getAllMicroactions(),
                      "usedMicroactionList": usedMicroactions_}
        self.__renderAndCreate("use_config", renderDict, tempDir_model / ("use_config_" + name_ + ".tex"))

        # Create pdf and copy to out sub-dir
        os.chdir(tempDir_model)
        os.system("pdflatex %s/%s.tex > /dev/null" %(str(tempDir_model), name_))
        os.replace("%s/%s.pdf" %(str(tempDir_model), name_), "%s/%s_model.pdf" %(str(self.__getSubDir_out(name_)), name_))
