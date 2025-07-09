/*********************************** Variants ***********************************/

%for var_i in variants_:
Variant ${var_i.name} ${builder_.getVariantDef(var_i)}
%endfor