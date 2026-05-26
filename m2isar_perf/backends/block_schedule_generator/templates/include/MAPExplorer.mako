${builder_.getFileHeader()}

#ifndef ${builder_.getHeaderGuardPrefix()}_MAP_EXPLORER_H
#define ${builder_.getHeaderGuardPrefix()}_MAP_EXPLORER_H

#include "MAPExplorer.h"

#include "Channel.h"

#include "${builder_.getName()}_BlockSchedulingFunctions.h"

<% 
linkList = []
%>
% for mod_i in variant_.getBranchGroup().getAllModels():
% if mod_i.link not in linkList:
#include "${mod_i.link}"
<%
linkList.append(mod_i.link)
%>
% endif
% endfor

<% 
linkList = []
%>
% for gr_i in variant_.getAllResourceGroups():
% for mod_i in gr_i.getAllModels():
% if mod_i.link not in linkList:
#include "${mod_i.link}"
<%
linkList.append(mod_i.link)
%>
% endif
% endfor

% endfor
#include <cstdint>
#include <array>
#include <memory>

namespace ${builder_.getName()}{

/* BRANCH GROUP */

class ${builder_.getBranchGroupClassName()} : public MAP_Explorer::BranchGroupT<
% for mod_i in variant_.getBranchGroup().getAllModels():
${builder_.getModelClassName(mod_i)}${"" if loop.last else ","}
% endfor
>{

public:
    ${builder_.getBranchGroupClassName()}();
    void connectChannel(Channel*, int*);
};

/* RESOURCE GROUPS */

% for gr_i in variant_.getAllResourceGroups():
class ${builder_.getResourceGroupClassName(gr_i)} : public MAP_Explorer::ResourceGroupT<
% for mod_i in gr_i.getAllModels():
${builder_.getModelClassName(mod_i)}${"" if loop.last else ","}
% endfor
>{

public:
    ${builder_.getResourceGroupClassName(gr_i)}();
    void connectChannel(Channel*, int*);
};

% endfor

/* MAP EXPLORER */

using MAPExplorerBase = MAP_Explorer::MAPExplorer<${variant_.getNumResourceGroups()}, ${variant_.getNumCombinations()}, ${variant_.getNumResourceCombinations()}, ${variant_.getNumInstructions()}, ${variant_.getDimension()}, ${variant_.getMaxDynDelayPerInstr()}, ${variant_.getNumTimingVariables()}>;

class ${builder_.getName()}_MAPExplorer : public MAPExplorerBase{

public:

    using CombType = typename MAPExplorerBase::CombType;
    using DVecType = typename MAPExplorerBase::DVecType;
    using ResGroupEntryType = typename MAPExplorerBase::ResGroupEntryType;

    ${builder_.getName()}_MAPExplorer();
    ~${builder_.getName()}_MAPExplorer() = default;

    virtual void connectChannel(Channel*);

private:

    // Branch-Group
    static ${builder_.getBranchGroupClassName()} branchGroup;

    // Resource-Group
    static const std::array<MAP_Explorer::ResourceGroup*, ${variant_.getNumResourceGroups()}> resGroups;

    // Instr -> ResourceGroup LUT
    static const std::array<const ResGroupEntryType, ${variant_.getNumInstructions()}> resGroupLUT;

    // Delay-Vectors
    static std::array<DVecType, ${variant_.getNumResourceCombinations()}> delayVectors;

    // Combinations
    static std::array<CombType, ${variant_.getNumCombinations()}> combs;
};

} // namespace ${builder_.getName()}

#endif // ${builder_.getHeaderGuardPrefix()}_MAP_EXPLORER_H