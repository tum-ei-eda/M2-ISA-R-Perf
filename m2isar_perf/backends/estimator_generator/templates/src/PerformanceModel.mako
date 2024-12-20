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

#include "${variant_.name}_PerformanceModel.h"

#include <stdbool.h>
#include <string>
#include <sstream>
#include <algorithm>

#include "Channel.h"

#include "${variant_.name}_Channel.h"

% for resM_i in variant_.getAllResourceModels():
#include "${resM_i.link}"
%endfor
% for conM_i in variant_.getAllConnectorModels():
#include "${conM_i.link}"
%endfor

namespace ${variant_.name}{

void ${variant_.name}_PerformanceModel::connectChannel(Channel* channel_)
{
  ${variant_.name}_Channel* channel = static_cast<${variant_.name}_Channel*>(channel_);

  % for resM_i in variant_.getAllResourceModels():
  % for trVal_i in resM_i.getAllTraceValues():
  ${resM_i.name}.${trVal_i}_ptr = channel->${trVal_i};
  %endfor

  %endfor
  % for conM_i in variant_.getAllConnectorModels():
  % for trVal_i in conM_i.getAllTraceValues():
  ${conM_i.name}.${trVal_i}_ptr = channel->${trVal_i};
  %endfor

  %endfor
}

uint64_t ${variant_.name}_PerformanceModel::getCycleCount(void)
{
  return std::max({\
  <% firstIt = True %>\
  %for var_i in variant_.getAllTimingVariables():
  %if firstIt:
  ${var_i.name}.get()\
  <% firstIt = False %>\
  %else:
  , ${var_i.name}.get()\
  %endif
  %endfor
  });
}

std::string ${variant_.name}_PerformanceModel::getPipelineStream(void)
{
  std::stringstream ret_strs;
  <% firstIt = True%>
  %for var_i in variant_.getAllTimingVariables():
  %if firstIt:
  ret_strs << ${var_i.name}.get(); <% firstIt = False%>
  %else:
  ret_strs << "," << ${var_i.name}.get();
  %endif
  %endfor
  ret_strs << std::endl;
  return ret_strs.str();
}

std::string ${variant_.name}_PerformanceModel::getPrintHeader(void)
{
  std::stringstream ret_strs;
  <% firstIt = True %>
  %for var_i in variant_.getAllTimingVariables():
  %if firstIt:
  ret_strs << "${var_i.name}"; <% firstIt = False %>
  %else:
  ret_strs << "," << "${var_i.name}";
  %endif
  %endfor
  ret_strs << std::endl;
  return ret_strs.str();
}

} // namespace ${variant_.name}