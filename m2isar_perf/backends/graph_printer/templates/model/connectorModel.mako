<%!
## TODO: Get rid of this long path here!! Need something relative?
from backends.graph_printer.utils import str2latex
from backends.graph_printer.utils import conModInputNodeName
from backends.graph_printer.utils import conModOutputNodeName
%>

\node[connectorModel, below = \connectorModelOffset of \placeRef] (${connectorModel.name}) {${str2latex(connectorModel.name)}};

\renewcommand\placeRef{${connectorModel.name}.north}

% for in_i in range(numInputs):
\node[minimum height = ${1/numInputs}*\connectorModelHeight, minimum width = \connectorModelWidth, below] (${conModInputNodeName(connectorModel, in_i)}) at (\placeRef) {};
\renewcommand\placeRef{${conModInputNodeName(connectorModel, in_i)}.south}
% endfor

\renewcommand\placeRef{${connectorModel.name}.north}

% for out_i in range(numOutputs):
\node[minimum height = ${1/numOutputs}*\connectorModelHeight, minimum width = \connectorModelWidth, below] (${conModOutputNodeName(connectorModel, out_i)}) at (\placeRef) {};
\renewcommand\placeRef{${conModOutputNodeName(connectorModel, out_i)}.south}
% endfor
