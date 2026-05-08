${builder_.getFileHeader()}

#ifndef ${builder_.getHeaderGuardPrefix()}_MAP_EXPLORER_H
#define ${builder_.getHeaderGuardPrefix()}_MAP_EXPLORER_H

#include "MAPExplorer.h"

#include "Channel.h"

#include "${builder_.getName()}_BlockSchedulingFunctions.h"

% for mod_i in variant_.getBranchGroup().getAllModels():
#include "${mod_i.link}"
% endfor

% for gr_i in variant_.getAllResourceGroups():
% for mod_i in gr_i.getAllModels():
#include "${mod_i.link}"

% endfor
% endfor
#include <cstdint>
#include <array>
#include <memory>

namespace ${builder_.getName()}{

/* BRANCH GROUP */

class ${builder_.getBranchGroupClassName()} : public MAP_Explorer::BranchGroup{

public:
    ${builder_.getBranchGroupClassName()}();
    ~${builder_.getBranchGroupClassName()}() = default;

    void connectChannel(Channel*, int*);

private:
    static const std::array<const map_models::BranchModel*, ${variant_.getBranchGroup().getNumModels()}> models;
};

/* RESOURCE GROUPS */

% for gr_i in variant_.getAllResourceGroups():
class ${builder_.getResourceGroupClassName(gr_i)} : public MAP_Explorer::ResourceGroup{

public:
    ${builder_.getResourceGroupClassName(gr_i)}();
    ~${builder_.getResourceGroupClassName(gr_i)}() = default;

    virtual void connectChannel(Channel*, int*);

private:
    mutable uint64_t delayBuffer[${gr_i.getNumModels()}] = {0};

    static const std::array<const map_models::ResourceModel*, ${gr_i.getNumModels()}> models;
};

% endfor

/* MAP EXPLORER */

using MAPExplorerBase = MAP_Explorer::MAPExplorer<${variant_.getNumResourceGroups()}, ${variant_.getNumCombinations()}, ${variant_.getNumInstructions()}, ${variant_.getDimension()}>;

class ${builder_.getName()}_MAPExplorer : public MAPExplorerBase{

public:

    using CombType = typename MAPExplorerBase::CombType;

    ${builder_.getName()}_MAPExplorer();
    ~${builder_.getName()}_MAPExplorer() = default;

    virtual void connectChannel(Channel*);

private:

    // Branch-Group
    static ${builder_.getBranchGroupClassName()} branchGroup;

    // Resource-Group
    static const std::array<const std::unique_ptr<MAP_Explorer::ResourceGroup>, ${variant_.getNumResourceGroups()}> resGroups;

    // Instruction -> ResourceGroup LUT
    static const std::array<const std::vector<int>, ${variant_.getNumInstructions()}> instrResLUT;

    // Combinations
    static const std::array<const CombType*, ${variant_.getNumCombinations()}> combs;
};

} // namespace ${builder_.getName()}

#endif // ${builder_.getHeaderGuardPrefix()}_MAP_EXPLORER_H