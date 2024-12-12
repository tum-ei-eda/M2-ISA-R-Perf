
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
\node[minimum height = \coreTitleHeight, below] (${printHelper_.elementTitle(corePerfModel)}) at (${corePerfModel.name}.north) {${printHelper_.str2latex(corePerfModel.name)}}; 
\renewcommand\placeRef{${printHelper_.elementTitle(corePerfModel)}.south}

\node[pipeline, below] (${pipeline.name}) at (\placeRef) {};
\node[minimum height = \pipelineTitleHeight, below] (${printHelper_.elementTitle(pipeline)}) at (${pipeline.name}.north) {${printHelper_.str2latex(pipeline.name)}}; 
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
\draw (${printHelper_.conModOutputNodeName(conMod, conModOutputCntDict[conMod.name])}.west) -| (${printHelper_.inConLinkNodeName(uA)});
<% conModOutputCntDict[conMod.name] += 1 %>
% endif

% if outCon is not None:
<% conMod = outCon.getConnectorModel() %>
\draw[-stealth] (${printHelper_.outConLinkNodeName(uA)}) |- (${printHelper_.conModInputNodeName(conMod, conModInputCntDict[conMod.name])}.east);
<% conModInputCntDict[conMod.name] += 1 %>
% endif

%endfor

\end{tikzpicture}

\end{document}