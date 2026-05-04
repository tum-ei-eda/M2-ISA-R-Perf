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
    ${builder_.getBranchGroupClassName()}(): MAP_Explorer::BranchGroup(models.data(), models.size()) {};
    ~${builder_.getBranchGroupClassName()}() = default;

    void connectChannel(Channel*, int*);

private:
    % for mod_i in variant_.getBranchGroup().getAllModels():
    % if mod_i.hasConfig():
    inline static ${builder_.getModelClassName(mod_i)} ${mod_i.name} = []{
        ${builder_.getModelConfigName(mod_i)} cfg;
        % for key_i,val_i in mod_i.getAllConfigs():
        cfg.${key_i} = ${val_i};
        % endfor
        return ${builder_.getModelClassName(mod_i)}(cfg);
    }();
    % else:
    inline static ${builder_.getModelClassName(mod_i)} ${mod_i.name};
    % endif
    % endfor

    static inline const std::array<const map_models::BranchModel*, ${variant_.getBranchGroup().getNumModels()}> models = {
        % for mod_i in variant_.getBranchGroup().getAllModels():
        &${mod_i.name}${"" if loop.last else ","}
        % endfor
    };
};

/* RESOURCE GROUPS */

% for gr_i in variant_.getAllResourceGroups():
class ${builder_.getResourceGroupClassName(gr_i)} : public MAP_Explorer::ResourceGroup{

public:
    ${builder_.getResourceGroupClassName(gr_i)}(): MAP_Explorer::ResourceGroup(${gr_i.id}, delayBuffer, models.data(), models.size()) {};
    ~${builder_.getResourceGroupClassName(gr_i)}() = default;

    virtual void connectChannel(Channel*, int*);

private:
    mutable uint64_t delayBuffer[${gr_i.getNumModels()}] = {0};

    % for mod_i in gr_i.getAllModels():
    % if mod_i.hasConfig():
    inline static ${builder_.getModelClassName(mod_i)} ${mod_i.name} = []{
        ${builder_.getModelConfigName(mod_i)} cfg;
        % for key_i,val_i in mod_i.getAllConfigs():
        cfg.${key_i} = ${val_i};
        % endfor
        return ${builder_.getModelClassName(mod_i)}(cfg);
    }();
    % else:
    inline static ${builder_.getModelClassName(mod_i)} ${mod_i.name};
    % endif
    % endfor

    static inline const std::array<const map_models::ResourceModel*, ${gr_i.getNumModels()}> models ={
        %for mod_i in gr_i.getAllModels():
        &${mod_i.name}${"" if loop.last else ","}
        % endfor
    };
};

% endfor

/* MAP EXPLORER */

using MAPExplorerBase = MAP_Explorer::MAPExplorer<${variant_.getNumResourceGroups()}, ${variant_.getNumCombinations()}, ${variant_.getNumInstructions()}, ${variant_.getDimension()}, ${maxDynDelayCnt_}>;

class ${builder_.getName()}_MAPExplorer : public MAPExplorerBase{

public:

    using CombType = typename MAPExplorerBase::CombType;

    ${builder_.getName()}_MAPExplorer():
        MAPExplorerBase(&${builder_.getName()}_blockDict,
            instrResLUT,
            resGroups,
            &branchGroup,
            combs
        ) {};
    ~${builder_.getName()}_MAPExplorer() = default;

    virtual void connectChannel(Channel*);

private:

    // TODO: Move instantiation of CV32E40P_blockDict here too?

    // Instruction -> ResourceGroup LUT
    static inline const std::array<const std::vector<int>, ${variant_.getNumInstructions()}> instrResLUT ={{
        % for instr_i in variant_.getAllInstructions():
        {${", ".join(str(x.id) for x in instr_i.getRequiredResourceGroups())}}${"" if loop.last else ","}
        % endfor 
    }};

    // Branch-Group
    inline static ${builder_.getBranchGroupClassName()} branchGroup;

    // Resource-Group
    static inline const std::array<const std::unique_ptr<MAP_Explorer::ResourceGroup>, ${variant_.getNumResourceGroups()}> resGroups = {
        % for gr_i in variant_.getAllResourceGroups():
        std::make_unique<${builder_.getResourceGroupClassName(gr_i)}>()${"" if loop.last else ","}
        % endfor
    };

    // Combinations
    % for comb_i in variant_.getAllCombinations():
    inline static const CombType comb_${comb_i.id} { {${", ".join( str(x.id) for x in comb_i.getAllResourceModels())}}, ${comb_i.getBranchModel().id} };
    % endfor 

    static inline const std::array<const CombType*, ${variant_.getNumCombinations()}> combs = {
        % for comb_i in variant_.getAllCombinations():
        &comb_${comb_i.id}${"" if loop.last else ","}
        % endfor
    };
};

} // namespace ${builder_.getName()}

#endif // ${builder_.getHeaderGuardPrefix()}_MAP_EXPLORER_H