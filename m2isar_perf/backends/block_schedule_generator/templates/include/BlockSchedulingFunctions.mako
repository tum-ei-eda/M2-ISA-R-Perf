${builder_.getFileHeader()}

#ifndef ${builder_.getHeaderGuardPrefix()}_BLOCK_SCHEDULING_FUNCTIONS_H
#define ${builder_.getHeaderGuardPrefix()}_BLOCK_SCHEDULING_FUNCTIONS_H

#include "BlockSchedulingFunctions.h"

#include <array>

namespace ${builder_.getName()}{

class ${builder_.getName()}_BlockDictionary : public MAP_Explorer::BlockDictionary{

public:
    ${builder_.getName()}_BlockDictionary(const std::array<MAP_Explorer::Block, ${size_}>& blocks_) : blocks(blocks_) {};

    const MAP_Explorer::Block* getBlock(uint64_t pc_) const override {
        for (const auto& blk_i : blocks){
            if(blk_i.startPc == pc_){
                return &blk_i;
            }
        }
        return nullptr;
    };

private:
    std::array<MAP_Explorer::Block, ${size_}> blocks;

};

extern const ${builder_.getName()}_BlockDictionary ${builder_.getName()}_blockDict;

} // namespace ${builder_.getName()}

#endif // ${builder_.getHeaderGuardPrefix()}_BLOCK_SCHEDULING_FUNCTIONS_H