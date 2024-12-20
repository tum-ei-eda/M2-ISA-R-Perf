/*
 * Copyright 2022 Chair of EDA, Technical University of Munich
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *	 http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/********************* AUTO GENERATE FILE (create by M2-ISA-R-Perf) *********************/

#ifndef ${builder_.getHeaderDefinePrefix(corePerfModel_)}_PERFORMANCE_MODEL_H
#define ${builder_.getHeaderDefinePrefix(corePerfModel_)}_PERFORMANCE_MODEL_H

#include <stdbool.h>
#include <string>
#include <cstdint>

#include "PerformanceModel.h"
#include "Channel.h"

% for resM_i in corePerfModel_.getAllResourceModels():
#include "${resM_i.link}"
%endfor
% for conM_i in corePerfModel_.getAllConnectorModels():
#include "${conM_i.link}"
%endfor

namespace ${corePerfModel_.name}{

class ${corePerfModel_.getPipeline().name}_Model
{
public:
  ${corePerfModel_.getPipeline().name}_Model(){};

  stage stages[${len(corePerfModel_.getAllStages())}] = { <% firstIt = True %>
  %for st_i in corePerfModel_.getAllStages():
    %if firstIt:
     stage("${st_i.name}") <% firstIt = False %>
    %else:
    ,stage("${st_i.name}")
    %endif
  %endfor
  };

  % for i, st_i in enumerate(corePerfModel_.getAllStages()):
  void set${st_i.name}(uint64_t c) { stages[${i}].cnt = c; };
  uint64_t get${st_i.name}(void) { return stages[${i}].cnt; };
  %if i == len(corePerfModel_.getAllStages()) - 1:

  uint64_t getCycleCount(void) { return stages[${i}].cnt; };
  %endif
  
  % endfor 
};


extern InstructionModelSet* ${corePerfModel_.name}_InstrModelSet;

class ${corePerfModel_.name}_PerformanceModel : public PerformanceModel
{
public:

  ${corePerfModel_.name}_PerformanceModel() : PerformanceModel("${corePerfModel_.name}", ${corePerfModel_.name}_InstrModelSet)
    ,${corePerfModel_.getPipeline().name}()
    % for resM_i in corePerfModel_.getAllResourceModels():
    ,${resM_i.name}(this)
    %endfor
    % for conM_i in corePerfModel_.getAllConnectorModels():
    ,${conM_i.name}(this)
    %endfor
  {};

  ${corePerfModel_.getPipeline().name}_Model ${corePerfModel_.getPipeline().name};

  %for resM_i in corePerfModel_.getAllResourceModels():
  ${builder_.getModelType(resM_i.link)} ${resM_i.name};
  %endfor

  %for conM_i in corePerfModel_.getAllConnectorModels():
  ${builder_.getModelType(conM_i.link)} ${conM_i.name};
  %endfor

  virtual void connectChannel(Channel*);
  virtual uint64_t getCycleCount(void){ return ${corePerfModel_.getPipeline().name}.getCycleCount(); };
  virtual std::string getPipelineStream(void);
  virtual std::string getPrintHeader(void);

};

} // namespace ${corePerfModel_.name}

#endif // ${builder_.getHeaderDefinePrefix(corePerfModel_)}_PERFORMANCE_MODEL_H