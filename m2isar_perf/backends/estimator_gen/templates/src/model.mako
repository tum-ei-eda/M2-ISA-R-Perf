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

#include "${corePerfModel_.name}_PerformanceModel.h"

#include <stdbool.h>
#include <string>
#include <sstream>

#include "Channel.h"

#include "${corePerfModel_.name}_Channel.h"

% for resM_i in corePerfModel_.getAllResourceModels():
#include "${resM_i.link}"
%endfor
% for conM_i in corePerfModel_.getAllConnectorModels():
#include "${conM_i.link}"
%endfor

void ${corePerfModel_.name}_PerformanceModel::connectChannel(Channel* channel_)
{
  ${corePerfModel_.name}_Channel* channel = static_cast<${corePerfModel_.name}_Channel*>(channel_);	

  % for resM_i in corePerfModel_.getAllResourceModels():
  % for trV_i in resM_i.traceValues:
  ${resM_i.name}.${trV_i}_ptr = channel->${trV_i};
  % endfor
  
  % endfor
  % for conM_i in corePerfModel_.getAllConnectorModels():
  % for trV_i in conM_i.traceValues:
  ${conM_i.name}.${trV_i}_ptr = channel->${trV_i};
  % endfor
  
  % endfor
}

std::string ${corePerfModel_.name}_PerformanceModel::getPipelineStream(void)
{
  std::stringstream ret_strs;
  <% firstIt = True %>
  %for st_i in corePerfModel_.getAllStages():
  %if firstIt:
  ret_strs << ${corePerfModel_.getPipeline().name}.get${st_i.name}(); <% firstIt = False %>
  %else:
  ret_strs << "," << ${corePerfModel_.getPipeline().name}.get${st_i.name}();
  %endif
  %endfor
  return ret_strs.str();
}

std::string ${corePerfModel_.name}_PerformanceModel::getPrintHeader(void)
{
  std::stringstream ret_strs;
  <% firstIt = True%>
  %for st_i in corePerfModel_.getAllStages():
  %if firstIt:
  ret_strs << "${st_i.name}"; <% firstIt = False %>
  %else:
  ret_strs << "," << "${st_i.name}";
  %endif
  %endfor
  return ret_strs.str();
}