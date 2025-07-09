/*********************************** External Models ***********************************/
TraceValue {
%for i, trVal_i in enumerate(traceValues_):
     ${trVal_i.name}${"," if i < len(traceValues_)-1 else ""}
%endfor
}

%for model_i in modelDict_:
Model ${model_i} ${builder_.getModelAttr(modelDict_[model_i])} ${builder_.getModelDef(modelDict_[model_i])}

%endfor
