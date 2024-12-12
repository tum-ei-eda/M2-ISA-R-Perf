
\node[connectorModel, below = \connectorModelOffset of \placeRef] (${connectorModel.name}) {${printHelper_.str2latex(connectorModel.name)}};

\renewcommand\placeRef{${connectorModel.name}.north}

% for in_i in range(numInputs):
\node[minimum height = ${1/numInputs}*\connectorModelHeight, minimum width = \connectorModelWidth, below] (${printHelper_.conModInputNodeName(connectorModel, in_i)}) at (\placeRef) {};
\renewcommand\placeRef{${printHelper_.conModInputNodeName(connectorModel, in_i)}.south}
% endfor

\renewcommand\placeRef{${connectorModel.name}.north}

% for out_i in range(numOutputs):
\node[minimum height = ${1/numOutputs}*\connectorModelHeight, minimum width = \connectorModelWidth, below] (${printHelper_.conModOutputNodeName(connectorModel, out_i)}) at (\placeRef) {};
\renewcommand\placeRef{${printHelper_.conModOutputNodeName(connectorModel, out_i)}.south}
% endfor
