/*********************************** Microactions ***********************************/

%if connectorDict_:
Connector {
%for i, con_i in enumerate(connectorDict_):
     ${con_i}${',' if i < len(connectorDict_)-1 else ''}
%endfor
}
%endif

Resource {
%for i, res_i in enumerate(resourceDict_):
     ${res_i} ${builder_.getResourceDef(resourceDict_[res_i])}${',' if i < len(resourceDict_)-1 else ''}
%endfor
}

%if virtualResources_:
virtual Resource {
%for i, vRes_i in enumerate(virtualResource_):
     ${vRes_i}${',' if i < len(virtualResource_)-1 else ''}
%endfor
}
%endif

Microaction {
%for i, uA_i in enumerate(microactionDict_):
     ${uA_i} ${builder_.getMicroactionDef(microactionDict_[uA_i])}${',' if i < len(microactionDict_)-1 else ''}
%endfor
}

%if virtualMicroactions_:
virtual Microaction {
%for i, vuA_i in enumerate(virtualMicroactions_):
     ${vuA_i}${',' if i < len(virtualMicroactions_)-1 else ''}
%endfor
}
%endif

