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
import errno
import os
import shutil

def createOrReplaceDir(dir_, suppress_warning=False):
    try:
        pathlib.Path(dir_).mkdir(parents=True)
    except OSError as e:
        if e.errno == errno.EEXIST:
            if not suppress_warning:
                print("WARNING: Following directory exists and is replaced: %s" %str(dir_)) 
            shutil.rmtree(dir_)
            pathlib.Path(dir_).mkdir(parents=True)
        else:
            raise
    return dir_

def getCodeDirPath(basePath_, variant_, compName_):
    return getArchDirPath(basePath_, variant_.getParentModel()) / ("code/" + compName_ + "/" + variant_.name)
    
def getDocDirPath(basePath_, variant_):
    return getArchDirPath(basePath_, variant_.getParentModel()) / ("doc/" + variant_.name)
    
def getMonitorFilePath(basePath_, model_):
    return getArchDirPath(basePath_, model_) / (model_.name  + "_trace.json")

def getArchDirPath(basePath_, model_):
    return basePath_ / model_.name

def getOverviewDirName():
    return "overview"
