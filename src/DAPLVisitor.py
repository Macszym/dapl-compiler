# Generated from DAPL.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .DAPLParser import DAPLParser
else:
    from DAPLParser import DAPLParser

# This class defines a complete generic visitor for a parse tree produced by DAPLParser.

class DAPLVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by DAPLParser#start.
    def visitStart(self, ctx:DAPLParser.StartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#line.
    def visitLine(self, ctx:DAPLParser.LineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#im1.
    def visitIm1(self, ctx:DAPLParser.Im1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#im2.
    def visitIm2(self, ctx:DAPLParser.Im2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#statement.
    def visitStatement(self, ctx:DAPLParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#scope.
    def visitScope(self, ctx:DAPLParser.ScopeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#varDecDefaultValue.
    def visitVarDecDefaultValue(self, ctx:DAPLParser.VarDecDefaultValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#varDecInitValue.
    def visitVarDecInitValue(self, ctx:DAPLParser.VarDecInitValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#constDec.
    def visitConstDec(self, ctx:DAPLParser.ConstDecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#emptyListDec.
    def visitEmptyListDec(self, ctx:DAPLParser.EmptyListDecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#listDec.
    def visitListDec(self, ctx:DAPLParser.ListDecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#emptyTableDec.
    def visitEmptyTableDec(self, ctx:DAPLParser.EmptyTableDecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#tableDec.
    def visitTableDec(self, ctx:DAPLParser.TableDecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#tableDec2.
    def visitTableDec2(self, ctx:DAPLParser.TableDec2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#read_csv.
    def visitRead_csv(self, ctx:DAPLParser.Read_csvContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#saveTable.
    def visitSaveTable(self, ctx:DAPLParser.SaveTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#columnList.
    def visitColumnList(self, ctx:DAPLParser.ColumnListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#column.
    def visitColumn(self, ctx:DAPLParser.ColumnContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#table.
    def visitTable(self, ctx:DAPLParser.TableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#row.
    def visitRow(self, ctx:DAPLParser.RowContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#tableAction.
    def visitTableAction(self, ctx:DAPLParser.TableActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#fillterOp.
    def visitFillterOp(self, ctx:DAPLParser.FillterOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#applyOp.
    def visitApplyOp(self, ctx:DAPLParser.ApplyOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#addOp.
    def visitAddOp(self, ctx:DAPLParser.AddOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#addRow.
    def visitAddRow(self, ctx:DAPLParser.AddRowContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#dropOp.
    def visitDropOp(self, ctx:DAPLParser.DropOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#joinOp.
    def visitJoinOp(self, ctx:DAPLParser.JoinOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#joinOp2.
    def visitJoinOp2(self, ctx:DAPLParser.JoinOp2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#groupOp.
    def visitGroupOp(self, ctx:DAPLParser.GroupOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#agregation.
    def visitAgregation(self, ctx:DAPLParser.AgregationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#showOp.
    def visitShowOp(self, ctx:DAPLParser.ShowOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#funcDec.
    def visitFuncDec(self, ctx:DAPLParser.FuncDecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#paramList.
    def visitParamList(self, ctx:DAPLParser.ParamListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#param.
    def visitParam(self, ctx:DAPLParser.ParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#functionCall.
    def visitFunctionCall(self, ctx:DAPLParser.FunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#argList.
    def visitArgList(self, ctx:DAPLParser.ArgListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#returnStatement.
    def visitReturnStatement(self, ctx:DAPLParser.ReturnStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#print.
    def visitPrint(self, ctx:DAPLParser.PrintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#valueExpr.
    def visitValueExpr(self, ctx:DAPLParser.ValueExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#valueText.
    def visitValueText(self, ctx:DAPLParser.ValueTextContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#valueBoolExpr.
    def visitValueBoolExpr(self, ctx:DAPLParser.ValueBoolExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#null.
    def visitNull(self, ctx:DAPLParser.NullContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#bool.
    def visitBool(self, ctx:DAPLParser.BoolContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#parent.
    def visitParent(self, ctx:DAPLParser.ParentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#parens.
    def visitParens(self, ctx:DAPLParser.ParensContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#double.
    def visitDouble(self, ctx:DAPLParser.DoubleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#addSub.
    def visitAddSub(self, ctx:DAPLParser.AddSubContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#funcCallExpr.
    def visitFuncCallExpr(self, ctx:DAPLParser.FuncCallExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#minusExpr.
    def visitMinusExpr(self, ctx:DAPLParser.MinusExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#modulo.
    def visitModulo(self, ctx:DAPLParser.ModuloContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#plusExpr.
    def visitPlusExpr(self, ctx:DAPLParser.PlusExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#int.
    def visitInt(self, ctx:DAPLParser.IntContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#nameExpr.
    def visitNameExpr(self, ctx:DAPLParser.NameExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#mulDiv.
    def visitMulDiv(self, ctx:DAPLParser.MulDivContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#type.
    def visitType(self, ctx:DAPLParser.TypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#boolExpr.
    def visitBoolExpr(self, ctx:DAPLParser.BoolExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#orExpr.
    def visitOrExpr(self, ctx:DAPLParser.OrExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#andExpr.
    def visitAndExpr(self, ctx:DAPLParser.AndExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#notExpr.
    def visitNotExpr(self, ctx:DAPLParser.NotExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#primaryBoolExpr.
    def visitPrimaryBoolExpr(self, ctx:DAPLParser.PrimaryBoolExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#ifStatement.
    def visitIfStatement(self, ctx:DAPLParser.IfStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#elifStatement.
    def visitElifStatement(self, ctx:DAPLParser.ElifStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#elseStatement.
    def visitElseStatement(self, ctx:DAPLParser.ElseStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#whileStatement.
    def visitWhileStatement(self, ctx:DAPLParser.WhileStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#comparasion.
    def visitComparasion(self, ctx:DAPLParser.ComparasionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#forStatement.
    def visitForStatement(self, ctx:DAPLParser.ForStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#operator.
    def visitOperator(self, ctx:DAPLParser.OperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#assign.
    def visitAssign(self, ctx:DAPLParser.AssignContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DAPLParser#lambdaExpr.
    def visitLambdaExpr(self, ctx:DAPLParser.LambdaExprContext):
        return self.visitChildren(ctx)



del DAPLParser