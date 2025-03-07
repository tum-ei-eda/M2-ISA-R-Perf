# Generated from CorePerfDSL.g4 by ANTLR 4.9.3
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .CorePerfDSLParser import CorePerfDSLParser
else:
    from CorePerfDSLParser import CorePerfDSLParser

# This class defines a complete generic visitor for a parse tree produced by CorePerfDSLParser.

class CorePerfDSLVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by CorePerfDSLParser#top.
    def visitTop(self, ctx:CorePerfDSLParser.TopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#corePerfModel_sec.
    def visitCorePerfModel_sec(self, ctx:CorePerfDSLParser.CorePerfModel_secContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#externModel_sec.
    def visitExternModel_sec(self, ctx:CorePerfDSLParser.ExternModel_secContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#instruction_sec.
    def visitInstruction_sec(self, ctx:CorePerfDSLParser.Instruction_secContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#connectorModel_def.
    def visitConnectorModel_def(self, ctx:CorePerfDSLParser.ConnectorModel_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#connectorModel.
    def visitConnectorModel(self, ctx:CorePerfDSLParser.ConnectorModelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#resourceModel_def.
    def visitResourceModel_def(self, ctx:CorePerfDSLParser.ResourceModel_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#resourceModel.
    def visitResourceModel(self, ctx:CorePerfDSLParser.ResourceModelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#model_def.
    def visitModel_def(self, ctx:CorePerfDSLParser.Model_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#model_list.
    def visitModel_list(self, ctx:CorePerfDSLParser.Model_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#model.
    def visitModel(self, ctx:CorePerfDSLParser.ModelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#traceValueMapping_def.
    def visitTraceValueMapping_def(self, ctx:CorePerfDSLParser.TraceValueMapping_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#traceValueMapping.
    def visitTraceValueMapping(self, ctx:CorePerfDSLParser.TraceValueMappingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#traceValue_def.
    def visitTraceValue_def(self, ctx:CorePerfDSLParser.TraceValue_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#traceValue.
    def visitTraceValue(self, ctx:CorePerfDSLParser.TraceValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#microactionMapping_def.
    def visitMicroactionMapping_def(self, ctx:CorePerfDSLParser.MicroactionMapping_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#microactionMapping.
    def visitMicroactionMapping(self, ctx:CorePerfDSLParser.MicroactionMappingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#instrGroup_def.
    def visitInstrGroup_def(self, ctx:CorePerfDSLParser.InstrGroup_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#instrGroup.
    def visitInstrGroup(self, ctx:CorePerfDSLParser.InstrGroupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#corePerfModel_def.
    def visitCorePerfModel_def(self, ctx:CorePerfDSLParser.CorePerfModel_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#corePerfModel.
    def visitCorePerfModel(self, ctx:CorePerfDSLParser.CorePerfModelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#pipeline_def.
    def visitPipeline_def(self, ctx:CorePerfDSLParser.Pipeline_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#pipeline_list.
    def visitPipeline_list(self, ctx:CorePerfDSLParser.Pipeline_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#pipeline.
    def visitPipeline(self, ctx:CorePerfDSLParser.PipelineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#pipeline_sequential.
    def visitPipeline_sequential(self, ctx:CorePerfDSLParser.Pipeline_sequentialContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#pipeline_parallel.
    def visitPipeline_parallel(self, ctx:CorePerfDSLParser.Pipeline_parallelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#pipeline_attr.
    def visitPipeline_attr(self, ctx:CorePerfDSLParser.Pipeline_attrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#stage_def.
    def visitStage_def(self, ctx:CorePerfDSLParser.Stage_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#stage_list.
    def visitStage_list(self, ctx:CorePerfDSLParser.Stage_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#stage.
    def visitStage(self, ctx:CorePerfDSLParser.StageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#stage_attr.
    def visitStage_attr(self, ctx:CorePerfDSLParser.Stage_attrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#microaction_def.
    def visitMicroaction_def(self, ctx:CorePerfDSLParser.Microaction_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#microaction_list.
    def visitMicroaction_list(self, ctx:CorePerfDSLParser.Microaction_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#microaction.
    def visitMicroaction(self, ctx:CorePerfDSLParser.MicroactionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#microactionComponent.
    def visitMicroactionComponent(self, ctx:CorePerfDSLParser.MicroactionComponentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#microactionComponent_list.
    def visitMicroactionComponent_list(self, ctx:CorePerfDSLParser.MicroactionComponent_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#connector_def.
    def visitConnector_def(self, ctx:CorePerfDSLParser.Connector_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#connector.
    def visitConnector(self, ctx:CorePerfDSLParser.ConnectorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#resource_def.
    def visitResource_def(self, ctx:CorePerfDSLParser.Resource_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#resource_list.
    def visitResource_list(self, ctx:CorePerfDSLParser.Resource_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#resource.
    def visitResource(self, ctx:CorePerfDSLParser.ResourceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#virtual_def.
    def visitVirtual_def(self, ctx:CorePerfDSLParser.Virtual_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#resource_assign.
    def visitResource_assign(self, ctx:CorePerfDSLParser.Resource_assignContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#microaction_assign.
    def visitMicroaction_assign(self, ctx:CorePerfDSLParser.Microaction_assignContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#traceValue_assign.
    def visitTraceValue_assign(self, ctx:CorePerfDSLParser.TraceValue_assignContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#connector_ref.
    def visitConnector_ref(self, ctx:CorePerfDSLParser.Connector_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#traceValue_ref.
    def visitTraceValue_ref(self, ctx:CorePerfDSLParser.TraceValue_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#resourceModel_ref.
    def visitResourceModel_ref(self, ctx:CorePerfDSLParser.ResourceModel_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#connectorModel_ref.
    def visitConnectorModel_ref(self, ctx:CorePerfDSLParser.ConnectorModel_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#model_ref.
    def visitModel_ref(self, ctx:CorePerfDSLParser.Model_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#resource_ref.
    def visitResource_ref(self, ctx:CorePerfDSLParser.Resource_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#resourceOrConnector_ref.
    def visitResourceOrConnector_ref(self, ctx:CorePerfDSLParser.ResourceOrConnector_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#microaction_ref.
    def visitMicroaction_ref(self, ctx:CorePerfDSLParser.Microaction_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#instructionOrInstrGroup_ref.
    def visitInstructionOrInstrGroup_ref(self, ctx:CorePerfDSLParser.InstructionOrInstrGroup_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#stage_ref.
    def visitStage_ref(self, ctx:CorePerfDSLParser.Stage_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#pipeline_ref.
    def visitPipeline_ref(self, ctx:CorePerfDSLParser.Pipeline_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#microactionOrPipeline_ref.
    def visitMicroactionOrPipeline_ref(self, ctx:CorePerfDSLParser.MicroactionOrPipeline_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#stageOrPipeline_ref.
    def visitStageOrPipeline_ref(self, ctx:CorePerfDSLParser.StageOrPipeline_refContext):
        return self.visitChildren(ctx)



del CorePerfDSLParser