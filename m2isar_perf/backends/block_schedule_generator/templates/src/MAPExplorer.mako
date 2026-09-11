${builder_.getFileHeader()}

#include "${builder_.getName()}_MAPExplorer.h"

#include "Channel.h"

#include "${builder_.getName()}_Channel.h"

#include "${builder_.getName()}_BlockSchedulingFunctions.h"
#include "${builder_.getName()}_InstructionSchedulingFunctions.h"

#include <array>
#include <cstddef>
#include <cstdint>

namespace ${builder_.getName()}{

/* BRANCH GROUP */

% for mod_i in variant_.getBranchGroup().getAllModels():
% if mod_i.hasConfig():
static ${builder_.getModelClassName(mod_i)} create_${mod_i.name}()
{
    ${builder_.getModelConfigName(mod_i)} cfg;
    % for key_i,val_i in mod_i.getAllConfigs():
    cfg.${key_i} = ${val_i};
    % endfor
    return ${builder_.getModelClassName(mod_i)}(cfg);
}
static ${builder_.getModelClassName(mod_i)} ${mod_i.name} = create_${mod_i.name}();

% else:
static ${builder_.getModelClassName(mod_i)} ${mod_i.name};
% endif
% endfor

${builder_.getBranchGroupClassName()}::${builder_.getBranchGroupClassName()}()
    : BranchGroupT(
        % for mod_i in variant_.getBranchGroup().getAllModels():
        ${mod_i.name}${"" if loop.last else ","}
        % endfor
    )
{}

void ${builder_.getBranchGroupClassName()}::connectChannel(Channel* channel_, int* instrIdx_ptr_){
    ${builder_.getChannelClassName()}* channel = static_cast<${builder_.getChannelClassName()}*>(channel_);

    % for mod_i in variant_.getBranchGroup().getAllModels():
    ${mod_i.name}.connectInstrIdx(instrIdx_ptr_);
    % for trVal_i in mod_i.getAllTraceValues():
    ${mod_i.name}.${trVal_i}_ptr = channel->${trVal_i};
    % endfor

    % endfor
}

/* RESOURCE GROUPS */

% for gr_i in variant_.getAllResourceGroups():
// -- ${builder_.getResourceGroupClassName(gr_i)}

% for mod_i in gr_i.getAllModels():
% if mod_i.hasConfig():
static ${builder_.getModelClassName(mod_i)} create_${mod_i.name}()
{
    ${builder_.getModelConfigName(mod_i)} cfg;
    % for key_i,val_i in mod_i.getAllConfigs():
    cfg.${key_i} = ${val_i};
    % endfor
    return ${builder_.getModelClassName(mod_i)}(cfg);
}
static ${builder_.getModelClassName(mod_i)} ${mod_i.name} = create_${mod_i.name}();

% else:
static ${builder_.getModelClassName(mod_i)} ${mod_i.name};
% endif
% endfor

${builder_.getResourceGroupClassName(gr_i)}::${builder_.getResourceGroupClassName(gr_i)}()
    : ResourceGroupT(
        ${gr_i.id},
        % for mod_i in gr_i.getAllModels():
        ${mod_i.name}${"" if loop.last else ","}
        % endfor
    )
{}

void ${builder_.getResourceGroupClassName(gr_i)}::connectChannel(Channel* channel_, int* instrIdx_ptr_){
    ${builder_.getChannelClassName()}* channel = static_cast<${builder_.getChannelClassName()}*>(channel_);

    % for mod_i in gr_i.getAllModels():
    ${mod_i.name}.connectInstrIdx(instrIdx_ptr_);
    % for trVal_i in mod_i.getAllTraceValues():
    ${mod_i.name}.${trVal_i}_ptr = channel->${trVal_i};
    % endfor

    % endfor
}

% endfor

/* MAP-EXPLORER */

// TODO: Need to restructure this code
// a) Duplication of code for USE_BLK true/false
// b) Static objects are constructed even if MAPExplorer is not used

// delayVectors and combs used to be emitted as fully-enumerated std::array
// aggregate initializers (one source line per element). For large design
// spaces that is tens of thousands of lines, which the compiler parses and
// optimizes extremely slowly (minutes, multiple GB of RAM at -O2).
//
// Instead we emit the same data in a compact form and rebuild the arrays at
// static-init time by calling the SAME element constructors in the SAME order.
// Runtime is unaffected (identical objects, layout and construction side
// effects); only a one-time fill loop is added. This is fully generic over the
// number of resource groups and the number of models per group.
namespace {

// One model pointer per (resource combination, resource group); group order
// matches the order DVecType expects.
static map_models::ResourceModel* const dvecModels[${variant_.getNumResourceCombinations()}][${variant_.getNumResourceGroups()}] = {
    % for resComb_i in variant_.getAllResourceCombinations():
    {${", ".join("&" + str(x.name) for x in resComb_i.getAllResourceModels())}}${"" if loop.last else ","}
    % endfor
};

// Branch model table, indexed by BranchModel::id.
static map_models::BranchModel* const branchModels[${variant_.getBranchGroup().getNumModels()}] = {
    % for mod_i in variant_.getBranchGroup().getAllModels():
    &${mod_i.name}${"" if loop.last else ","}
    % endfor
};

// Per combination: which resource combination and which branch model.
// Stored as plain indices (no per-element constructors / address constants),
// which is what makes this cheap to parse compared to the old aggregate.
static const std::uint32_t combResCombIdx[${variant_.getNumCombinations()}] = {
    % for comb_i in variant_.getAllCombinations():
    ${comb_i.getResourceCombination().id}${"" if loop.last else ","}
    % endfor
};
static const std::uint32_t combBranchIdx[${variant_.getNumCombinations()}] = {
    % for comb_i in variant_.getAllCombinations():
    ${comb_i.getBranchModel().id}${"" if loop.last else ","}
    % endfor
};

// Plain loop builders. The arrays are default-constructed and then every
// element is overwritten with its real value, so the resulting state is
// identical to the old fully-enumerated tables. (This relies on DVecType and
// CombType being default-constructible.)
template <bool BLK>
std::array<typename ${builder_.getName()}_MAPExplorer<BLK>::DVecType, ${variant_.getNumResourceCombinations()}>
buildDelayVectors() {
    std::array<typename ${builder_.getName()}_MAPExplorer<BLK>::DVecType, ${variant_.getNumResourceCombinations()}> dvecs;
    for (std::size_t i = 0; i < ${variant_.getNumResourceCombinations()}; ++i) {
        std::array<map_models::ResourceModel*, ${variant_.getNumResourceGroups()}> models{};
        for (std::size_t g = 0; g < ${variant_.getNumResourceGroups()}; ++g) {
            models[g] = dvecModels[i][g];
        }
        dvecs[i] = typename ${builder_.getName()}_MAPExplorer<BLK>::DVecType(models);
    }
    return dvecs;
}

// delayVectors is a private static member, so it is passed in from the
// member-definition context (which has access) rather than read directly here.
template <bool BLK>
std::array<typename ${builder_.getName()}_MAPExplorer<BLK>::CombType, ${variant_.getNumCombinations()}>
buildCombs(std::array<typename ${builder_.getName()}_MAPExplorer<BLK>::DVecType, ${variant_.getNumResourceCombinations()}>& dvecs) {
    std::array<typename ${builder_.getName()}_MAPExplorer<BLK>::CombType, ${variant_.getNumCombinations()}> combs;
    for (std::size_t k = 0; k < ${variant_.getNumCombinations()}; ++k) {
        combs[k] = typename ${builder_.getName()}_MAPExplorer<BLK>::CombType(&dvecs[combResCombIdx[k]], branchModels[combBranchIdx[k]]);
    }
    return combs;
}

} // anonymous namespace

% for i, useBlk_i in enumerate(["true", "false"]):
// USE_BLK: ${useBlk_i}

template<>
${builder_.getBranchGroupClassName()} ${builder_.getName()}_MAPExplorer<${useBlk_i}>::branchGroup = ${builder_.getBranchGroupClassName()}();

% if i==0:
% for gr_i in variant_.getAllResourceGroups():
static ${builder_.getResourceGroupClassName(gr_i)} resGroup_${gr_i.name};
% endfor
% endif

template<>
constexpr std::array<MAP_Explorer::ResourceGroup*, ${variant_.getNumResourceGroups()}>
${builder_.getName()}_MAPExplorer<${useBlk_i}>::resGroups = {
    %for gr_i in variant_.getAllResourceGroups():
    &${builder_.getResourceGroupName(gr_i)}${"" if loop.last else ","}
    % endfor
};

template<>
constexpr std::array<const ${builder_.getName()}_MAPExplorer<${useBlk_i}>::ResGroupEntryType, ${variant_.getNumInstructions()}>
${builder_.getName()}_MAPExplorer<${useBlk_i}>::resGroupLUT = {{
    % for instr_i in variant_.getAllInstructions():
    {${instr_i.getNumDynDelays()},{${", ".join("&" + builder_.getResourceGroupName(x) for x in instr_i.getRequiredResourceGroups())}}}${"" if loop.last else ","}
    % endfor
}};

template<>
std::array<${builder_.getName()}_MAPExplorer<${useBlk_i}>::DVecType, ${variant_.getNumResourceCombinations()}>
${builder_.getName()}_MAPExplorer<${useBlk_i}>::delayVectors =
    buildDelayVectors<${useBlk_i}>();

template<>
std::array<${builder_.getName()}_MAPExplorer<${useBlk_i}>::CombType, ${variant_.getNumCombinations()}>
${builder_.getName()}_MAPExplorer<${useBlk_i}>::combs =
    buildCombs<${useBlk_i}>(${builder_.getName()}_MAPExplorer<${useBlk_i}>::delayVectors);

template<>
${builder_.getName()}_MAPExplorer<${useBlk_i}>::${builder_.getName()}_MAPExplorer()
    : MAPExplorerBase<${useBlk_i}>(
        &${builder_.getName()}_blockDict,
        &${builder_.getName()}_instrDict,
        resGroupLUT,
        resGroups,
        &branchGroup,
        delayVectors,
        combs) 
{}

template<>
void ${builder_.getName()}_MAPExplorer<${useBlk_i}>::connectChannel(Channel* channel_){
    ch_instrCnt_ptr = &(channel_->instrCnt);
    ch_typeId_ptr = channel_->typeId;

    // TODO: Currently hard-coded. Need to get this information from somewhere
    ${builder_.getChannelClassName()}* channel = static_cast<${builder_.getChannelClassName()}*>(channel_);
    ch_pc_ptr = channel->pc;
    ch_rs1_ptr = channel->rs1;
    ch_rs2_ptr = channel->rs2;
    ch_rd_ptr = channel->rd;

    branchGroup.connectChannel(channel_, &curInstrIdx);

    % for i in range(variant_.getNumResourceGroups()):
    resGroups[${i}]->connectChannel(channel_, &curInstrIdx);
    % endfor
}
% endfor

} // namespace ${builder_.getName()}