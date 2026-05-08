TARGET_SOURCES(SWEVAL_BACKENDS_LIB PRIVATE
    ${builder_.getName()}_BlockSchedulingFunctions.cpp
    % for i in range(splitCnt_):
    ${builder_.getName()}_BlockSchedules_${i}.cpp
    % endfor 
)