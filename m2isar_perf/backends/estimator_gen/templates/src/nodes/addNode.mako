int ${node_.getIdStr()};
% if node_.hasModel():
${node_.getIdStr()} = ${node_.getPrev().getIdStr()} + perfModel->${node_.getModel().name}.getDelay();\
% else:
${node_.getIdStr()} = ${node_.getPrev().getIdStr()} + ${node_.getDelay()};\
% endif