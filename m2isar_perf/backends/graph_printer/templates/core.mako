<%!
## TODO: Get rid of this long path here!! Need something relative?
from backends.graph_printer.utils import str2latex
from backends.graph_printer.utils import inConLinkNodeName
from backends.graph_printer.utils import outConLinkNodeName
from backends.graph_printer.utils import conModOutputNodeName
from backends.graph_printer.utils import conModInputNodeName
from backends.graph_printer.utils import elementTitle
%>

<%
pipeline = corePerfModel.getPipeline()
stageList = corePerfModel.getAllStages()
uAList = corePerfModel.getAllMicroactions()

conModInputCntDict = {}
conModOutputCntDict = {}
for conMod in corePerfModel.getAllConnectorModels():
    conModInputCntDict[conMod.name] = 0
    conModOutputCntDict[conMod.name] = 0
%>

\input{../size_config.tex}

\begin{document}

\begin{tikzpicture}

\node[core] (${corePerfModel.name}) at \placeRef {};
\node[minimum height = \coreTitleHeight, below] (${elementTitle(corePerfModel)}) at (${corePerfModel.name}.north) {${str2latex(corePerfModel.name)}}; 
\renewcommand\placeRef{${elementTitle(corePerfModel)}.south}

\node[pipeline, below] (${pipeline.name}) at (\placeRef) {};
\node[minimum height = \pipelineTitleHeight, below] (${elementTitle(pipeline)}) at (${pipeline.name}.north) {${str2latex(pipeline.name)}}; 
\renewcommand\placeRef{${pipeline.name}.west}

%for st in stageList:
\input{../stages/${st.name}.tex}
\renewcommand\placeRef{${st.name}}
%endfor

%for uA in uAList:
<% inCon = uA.getInConnector() %>
<% outCon = uA.getOutConnector() %>

% if inCon is not None:
<% conMod = inCon.getConnectorModel() %>
\draw (${conModOutputNodeName(conMod, conModOutputCntDict[conMod.name])}.west) -| (${inConLinkNodeName(uA)});
<% conModOutputCntDict[conMod.name] += 1 %>
% endif

% if outCon is not None:
<% conMod = outCon.getConnectorModel() %>
\draw[-stealth] (${outConLinkNodeName(uA)}) |- (${conModInputNodeName(conMod, conModInputCntDict[conMod.name])}.east);
<% conModInputCntDict[conMod.name] += 1 %>
% endif

%endfor

\end{tikzpicture}

\end{document}