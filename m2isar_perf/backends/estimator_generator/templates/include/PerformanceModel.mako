/*
 * Copyright 2024 Chair of EDA, Technical University of Munich
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

#ifndef ${builder_.getHeaderGuardPrefix()}_PERFORMANCE_MODEL_H
#define ${builder_.getHeaderGuardPrefix()}_PERFORMANCE_MODEL_H

#include <stdbool.h>
#include <string>
#include <cstdint>

#include "PerformanceModel.h"
#include "Channel.h"

% for resM_i in variant_.getAllResourceModels():
#include "${resM_i.link}"
%endfor
% for conM_i in variant_.getAllConnectorModels():
#include "${conM_i.link}"
%endfor

namespace ${variant_.name}{

extern SchedulingFunctionSet* ${variant_.name}_SchedulingFunctionSet;

class ${variant_.name}_PerformanceModel : public PerformanceModel
{
public:

  ${variant_.name}_PerformanceModel() : PerformanceModel("${variant_.name}", ${variant_.name}_SchedulingFunctionSet)
    % for tVar_i in variant_.getAllTimingVariables():
    ,${tVar_i.name}("${tVar_i.name}")
    %endfor
    % for resM_i in variant_.getAllResourceModels():
    ,${resM_i.name}(this)
    %endfor
    % for conM_i in variant_.getAllConnectorModels():
    ,${conM_i.name}(this)
    %endfor
  {};
  
  %for tVar_i in variant_.getAllTimingVariables():
  TimingVariable ${tVar_i.name};
  %endfor	 

  %for resM_i in variant_.getAllResourceModels():
  ${builder_.getModelType(resM_i.link)} ${resM_i.name};
  %endfor

  %for conM_i in variant_.getAllConnectorModels():
  ${builder_.getModelType(conM_i.link)} ${conM_i.name};
  %endfor

  virtual void connectChannel(Channel*);
  virtual uint64_t getCycleCount(void);
  virtual std::string getPipelineStream(void);
  virtual std::string getPrintHeader(void);

};

} // namespace ${variant_.name}

#endif // ${builder_.getHeaderGuardPrefix()}_PERFORMANCE_MODEL_H