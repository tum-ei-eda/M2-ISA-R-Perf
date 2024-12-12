
% for uA in microactionList:
% if uA in usedMicroactionList:
\newcommand\${printHelper_.str2latexCmd(uA.name)}Fill{gray}
% else:
\newcommand\${printHelper_.str2latexCmd(uA.name)}Fill{white}
% endif
% endfor