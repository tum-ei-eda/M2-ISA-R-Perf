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
            # TODO: Better handling here? Wait for user input?
            if not suppress_warning:
                #print("WARNING: %s folder exists and is replaced" %(os.path.basename(os.path.normpath(str(dir_)))))
                print("WARNING: Following directory exists and is replaced: %s" %str(dir_)) 
            shutil.rmtree(dir_)
            pathlib.Path(dir_).mkdir(parents=True)
        else:
            raise
    return dir_

def getCodeDirPath(basePath_, modelName_):
    return basePath_ / modelName_ / "code"

def getDocDirPath(basePath_, modelName_):
    return basePath_ / modelName_ / "doc"

def getMonitorDirPath(basePath_, modelName_):
    return basePath_ / modelName_

def getOverviewDirName():
    return "overview"
