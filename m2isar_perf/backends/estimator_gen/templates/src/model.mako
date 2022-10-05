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

#include "${corePerfModel_.name}_Model.h"

#include <stdbool.h>

#include "ArchInterface/TraceChannel.h"

#include "${corePerfModel_.name}_TraceChannel.h"

% for resM_i in corePerfModel_.getAllResourceModels():
#include "${resM_i.link}.h"
%endfor
% for conM_i in corePerfModel_.getAllConnectorModels():
#include "${conM_i.link}.h"
%endfor

namespace etiss // TODO: Rethink namespace organization
{

namespace plugin
{

namespace PerformanceEstimator
{

bool ${corePerfModel_.name}_Model::connectChannel(TraceChannel* channel_)
{
  SubChannel* subCh = channel_->getSubChannel("${corePerfModel_.name}_SubChannel");
  if(subCh == nullptr)
  {
    return false;
  }

  ${corePerfModel_.name}_SubChannel* channel = static_cast<${corePerfModel_.name}_SubChannel*>(subCh);

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

} // namespace PerformanceEstimator
} // namespace plugin
} // namespace etiss