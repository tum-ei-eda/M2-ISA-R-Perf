${builder_.getFileHeader()}

#include "BlockSchedulingFunctions.h"

#include <algorithm>

namespace ${builder_.getName()}{

% for blk_i in blocks_:

% for i, tStage_i in enumerate(blk_i.tempStages):
static inline void block_${blk_i.id}_tempStage_${i}(uint64_t* t, const uint8_t* d_){
${tStage_i}
}

% endfor

static void block_${blk_i.id}_fn(uint64_t* vec_, uint8_t* d_){
    % if blk_i.numTemps > 0:
    uint64_t t[${blk_i.numTemps}];
    % endif

    % for stage_i, _ in enumerate(blk_i.tempStages):
    block_${blk_i.id}_tempStage_${stage_i}(t, d_);
    % endfor

    ${blk_i.code}
}

extern const MAP_Explorer::Block block_${blk_i.id}{
    ${blk_i.id},
    ${blk_i.startPc},
    ${blk_i.endPc},
    ${str(blk_i.endsOnBranch).lower()},
    block_${blk_i.id}_fn
    };

% endfor

} // namespace ${builder_.getName()}