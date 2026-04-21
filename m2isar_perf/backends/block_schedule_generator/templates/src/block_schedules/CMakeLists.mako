TARGET_SOURCES(SWEVAL_BACKENDS_LIB PRIVATE
    % for i in range(splitCnt_):
    ${builder_.getName()}_BlockSchedules_${i}
    % endfor 
)