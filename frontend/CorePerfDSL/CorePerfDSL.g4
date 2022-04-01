grammar CorePerfDSL;
description_context : (corePerfModel_sec
		    | externModel_sec
		    | instruction_sec
		    )* EOF
;

corePerfModel_sec : virtual_def | connector_def | resource_def | microaction_def | stage_def | pipeline_def | corePerfModel_def ;
externModel_sec : traceValue_def | connectorModel_def | resourceModel_def ;
instruction_sec : instrGroup_def | microactionMapping_def ;

//////////////////////////// CONNECTOR_MODEL ////////////////////////////

connectorModel_def : 'ConnectorModel' (connectorModel | '{' connectorModel (',' connectorModel)* '}');

connectorModel : name=ID '(' (
	      'trace' ':' (traceVals+=traceValue_ref | '{' traceVals+=traceValue_ref (',' traceVals+=traceValue_ref)* '}')
	      | 'link' ':' link=ID
	      | 'connectorIn' ':' (inCons+=connector_ref | '{' inCons+=connector_ref (',' inCons+=connector_ref)* '}')
	      | 'connectorOut' ':' (outCons+=connector_ref | '{' outCons+=connector_ref (',' outCons+=connector_ref)* '}')
	      )* ')'
;

//////////////////////////// RESOURCE_MODEL ////////////////////////////

resourceModel_def : 'ResourceModel' (resourceModel | '{' resourceModel (',' resourceModel)* '}') ;

resourceModel : name=ID '(' (
	      'trace' ':' (traceVals+=traceValue_ref | '{' traceVals+=traceValue_ref (',' traceVals+=traceValue_ref)* '}')
	      | 'link' ':' link=ID
	      )* ')'
;

//////////////////////////// TRACE_VALUE ////////////////////////////

traceValue_def : 'TraceValue' (traceValue | '{' traceValue (',' traceValue)* '}');

traceValue : name=ID ;

//////////////////////////// MICROACTION_MAPPING ////////////////////////////

microactionMapping_def : 'MicroactionMapping' (microactionMapping | '{' microactionMapping (',' microactionMapping)* '}' );

microactionMapping : instr=instructionOrInstrGroup_ref ':' (microactions+=microaction_ref | '{' microactions+=microaction_ref (',' microactions+=microaction_ref)* '}');

//////////////////////////// INSTRUCTION_GROUP ////////////////////////////

instrGroup_def : 'InstrGroup' (instrGroup | '{' instrGroup (',' instrGroup)* '}');

instrGroup : name=ID '(' instructions+=instruction_ref (',' instructions+=instruction_ref)* ')'; // TODO: Special instr-reference instead of ID?

//////////////////////////// CORE_PERFORMANCE_MODEL ////////////////////////////

corePerfModel_def : 'CorePerfModel' (corePerfModel | '{' corePerfModel (',' corePerfModel)* '}');

corePerfModel : name=ID '(' (
      'use' 'Pipeline' ':' use_pipeline=pipeline_ref
      | 'use' 'ConnectorModel' ':' (conModels+=connectorModel_ref | '{' conModels+=connectorModel_ref (',' conModels+=connectorModel_ref)* '}')
      | 'assign' 'Resource' ':' ((vir_Res+=virResource_ref '=' nvir_Res+=nonVirResource_ref) | '{' (vir_Res+=virResource_ref '=' nvir_Res+=nonVirResource_ref) (',' (vir_Res+=virResource_ref '=' nvir_Res+=nonVirResource_ref))* '}')
      | 'assign' 'Microaction' ':' ((vir_uA+=virMicroaction_ref '=' nvir_uA+=nonVirMicroaction_ref) | '{' (vir_uA+=virMicroaction_ref '=' nvir_uA+=nonVirMicroaction_ref) (',' (vir_uA+=virMicroaction_ref '=' nvir_uA+=nonVirMicroaction_ref))* '}')
      )* ')'
;

//////////////////////////// PIPELINE ////////////////////////////

pipeline_def : 'Pipeline' (pipeline | '{' pipeline (',' pipeline)* '}');

pipeline : name=ID '(' stages+=stage_ref ('->' stages+=stage_ref)* ')';

//////////////////////////// STAGE ////////////////////////////

stage_def : 'Stage' (stage | '{' stage (',' stage)* '}');

stage : name=ID '(' microactions+=microaction_ref (',' microactions+=microaction_ref)* ')';

//////////////////////////// MICROACTION ////////////////////////////

microaction_def : 'Microaction' (microaction | '{' microaction (',' microaction)* '}');

microaction : name=ID '(' ref_1=resourceOrConnector_ref ')' # microaction_single_arg
	    | name=ID '(' ref_1=resourceOrConnector_ref '->' ref_2=resourceOrConnector_ref ')' # microaction_double_arg
	    | name=ID '(' ref_1=connector_ref '->' ref_2=resource_ref '->' ref_3=connector_ref ')' #microaction_triple_arg
;

//////////////////////////// CONNECTOR ////////////////////////////

connector_def : 'Connector' (connector | '{' connector (',' connector)* '}');

connector : name=ID;

//////////////////////////// RESOURCE ////////////////////////////

resource_def : 'Resource' (resource | '{' resource (',' resource)* '}');

resource : 
    name=ID '(' res_model=resourceModel_ref ')' # resource_model
    | name=ID '(' delay=INT ')' # resource_delay
    | name=ID # resource_default
;

//////////////////////////// VIRTUAL ////////////////////////////

virtual_def: 'virtual' (type_='Resource' | type_='Microaction') (virtuals+=virtual | '{' virtuals+=virtual (',' virtuals+=virtual)* '}');

virtual : name=ID ;

//////////////////////////// REFERENCES ////////////////////////////

instruction_ref : name=(ID|KEYWORD_REST);

connector_ref : name=ID ;

traceValue_ref : name=ID ; 

resourceModel_ref : name=ID ;

connectorModel_ref : name=ID ;

resource_ref : name=ID ;
virResource_ref : name=ID ;
nonVirResource_ref : name = ID;

resourceOrConnector_ref : name=ID ;

microaction_ref : name=ID ;
virMicroaction_ref : name=ID ;
nonVirMicroaction_ref : name=ID ;

instructionOrInstrGroup_ref : name=(ID|KEYWORD_ALL) ;

stage_ref : name=ID ;

pipeline_ref : name=ID ;

//////////////////////////// LEXER RULES ////////////////////////////

ID : [a-zA-Z] [a-zA-Z0-9_]*  ;
INT : [0-9][0-9]* ;

KEYWORD_ALL  : '[ALL]' ;
KEYWORD_REST : '[?]' ;

ML_COMMENT: '/*' .*? '*/' -> skip;
SL_COMMENT: '//' ~('\n'|'r')* ('r'? '\n')? -> skip;
WS: [ \t\r\n]+ -> skip;