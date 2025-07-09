/*********************************** Instruction Mappings ***********************************/

InstrGroup Default ([?])

MicroactionMapping {
%for i, instr_i in enumerate(microactionMappingDict_):
     ${builder_.getInstrName(instr_i)} : ${builder_.getMicroactionMapping(microactionMappingDict_[instr_i])}${"," if i < len(microactionMappingDict_)-1 else ""}
%endfor
}

TraceValueMapping {
%for i, instr_i in enumerate(instructions_):
     ${builder_.getInstrName(instr_i)} : ${builder_.getTraceValueMapping(instr_i)}${"," if i < len(instructions_)-1 else ""}
%endfor
}