${builder_.getFileHeader()}

#include "${builder_.getName()}_MAPExplorer.h"

#include "Channel.h"

#include "${builder_.getName()}_Channel.h"

namespace ${builder_.getName()}{

/* BRANCH GROUP */

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

void ${builder_.getName()}_MAPExplorer::connectChannel(Channel* channel_){
    ch_instrCnt_ptr = &(channel_->instrCnt);
    ch_typeId_ptr = channel_->typeId;

    // TODO: Currently hard-coded. Need to get this information from somewhere
    ${builder_.getChannelClassName()}* channel = static_cast<${builder_.getChannelClassName()}*>(channel_);
    ch_pc_ptr = channel->pc;

    branchGroup.connectChannel(channel_, &curInstrIdx);

    % for i in range(variant_.getNumResourceGroups()):
    resGroups[${i}]->connectChannel(channel_, &curInstrIdx);
    % endfor
}

} // namespace ${builder_.getName()}