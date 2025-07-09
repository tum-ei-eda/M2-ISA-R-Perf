/************************************ Stages & Pipeline ************************************/

Stage {
%for i, st_i in enumerate(stageDict_):
     ${st_i} ${builder_.getStageDef(stageDict_[st_i])}${',' if i < len(stageDict_)-1 else ''}
%endfor
}

Pipeline {
%for i, pipe_i in enumerate(pipelineDict_):
     ${pipe_i} ${builder_.getPipelineDef(pipelineDict_[pipe_i])}${',' if i < len(pipelineDict_)-1 else ''}
%endfor
}

