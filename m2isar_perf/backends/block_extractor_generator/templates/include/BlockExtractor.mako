${builder_.getFileHeader()}

#ifndef ${builder_.getHeaderGuardPrefix()}_BLOCK_EXTRACTOR_H
#define ${builder_.getHeaderGuardPrefix()}_BLOCK_EXTRACTOR_H

#include "BlockExtractor.h"

#include "${builder_.getName()}_BlockInstructionGenerator.h"

#include "Channel.h"

namespace ${builder_.getName()}{

class ${builder_.getName()}_BlockExtractor : public BlockExtractor{

public:
    ${builder_.getName()}_BlockExtractor(){
        blockInstrGen = std::make_unique<${builder_.getName()}_BlockInstructionGenerator>();
        outputPath = "${builder_.getName()}_BlockList.json";
    };
    ~${builder_.getName()}_BlockExtractor() = default;

    virtual void connectChannel(Channel* channel_){
        channel = channel_;
        ch_typeId_ptr = channel_->typeId;
        ch_instrCnt_ptr = &(channel_->instrCnt);

        ${builder_.getName()}_Channel* spec_channel = static_cast<${builder_.getName()}_Channel*>(channel_);
        ch_pc_ptr = spec_channel->${builder_.getPcTraceValue()};
    };

};

} // namespace ${builder_.getName()}

#endif // ${builder_.getHeaderGuardPrefix()}_BLOCK_EXTRACTOR_H