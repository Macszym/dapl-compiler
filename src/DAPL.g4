grammar DAPL;

start:  line+ EOF;

line:   im
    | dec
    | assign
    | print
    | statement
    | funcDec
    | tableAction
    | saveTable
    | BlockComment
    | LineComment;

im: 'import' NAME ';'   #im1
    | 'from' NAME 'import' NAME ';' #im2;

statement:  scope
    |   ifStatement
    |   whileStatement
    |   forStatement
    |   functionCall
    |   returnStatement;

scope:  '{' line* '}';

dec:
    'var' type ':' NAME ';'     #varDecDefaultValue
    | 'var' type ':' NAME '=' value ';'   #varDecInitValue
    | type ':' NAME '=' value ';' #constDec
    | 'List' '<' type '>' NAME ';' #emptyListDec
    | 'List' '<' type '>' NAME '=' row ';' #listDec
    | 'Table' '<' columnList '>' NAME ';'  #emptyTableDec
    | 'Table' '<' columnList '>' NAME '=' table ';'  #tableDec
    | 'Table' NAME '=' table ';'    #tableDec2
    | 'Table' NAME '=' 'read_csv' '(' TEXT ')' ';'   #read_csv;

saveTable: NAME '.' 'save' '(' TEXT ')';

columnList: column (',' column)*;

column: type ':' NAME;

table: '[' '[' row ']' (',' '[' row ']')* ']';

row:    value (',' value)*;

tableAction:
    NAME ('.' tableOperation)* ('.' terminalTableOperation)?;

tableOperation: 'filter' '(' INT ',' lambdaExpr ')'  #fillterOp
    | 'apply' '(' INT ',' lambdaExpr ')'    #applyOp
    | 'addColumn' '(' '<' columnList '>' ')'    #addOp
    | 'addRow' '(' '[' row ']' ')'  #addRow
    | 'drop' '(' INT ')'   #dropOp
    | 'join' '(' NAME ',' INT ',' INT ')'   #joinOp
    | 'join' '(' NAME ',' NAME ',' NAME ')'   #joinOp2
    | 'groupBy' '(' INT ',' INT ',' agregation')'   #groupOp;

agregation:
    'max'
    | 'min'
    | 'count'
    | 'average'
    | 'sum';

terminalTableOperation:
    'show' '()' ';'    #showOp;

funcDec:
    'function' NAME '(' paramList? ')' (':' (type | 'void'))? '{' line* '}';


paramList:
    param (',' param)*;

param:
    type ':' NAME;

functionCall:
    NAME '(' argList? ')' ';';

argList:
    value (',' value)*;

returnStatement:
    'return' (':' value)? ';';

//printowanie
print: 'out' '(' value ')' ';';

//value - to co printujemy lub przypisujemy
value:  expr    #valueExpr
    | TEXT  #valueText
    | boolExpr  #valueBoolExpr
    | 'null'    #null;

bool:   'true'
    |   'false';

//wyrażenie matematyczne
expr
    : expr op=('*'|'/'|'/!') expr         # mulDiv
    | expr op=('+'|'-') expr         # addSub
    | expr '%' expr                  # modulo
    | '(' expr ')'                   # parens
    | '-' expr                       # minusExpr
    | '+' expr                       # plusExpr
    | NAME '(' (value (',' value)*)? ')'   # funcCallExpr
    | INT                            # int
    | DOUBLE                         # double
    | NAME                           # nameExpr
    | ('^')+ NAME                    # parent
    ;

type:   'int'
    | 'double'
    | 'char'
    | 'string'
    | 'bool'
    | 'auto';

//wyrażenia logiczne
boolExpr:   orExpr;

orExpr: andExpr (OR andExpr)* ;

andExpr:    notExpr (AND notExpr)* ;

notExpr:    NOT? primaryBoolExpr;

primaryBoolExpr:    bool
    |   NAME
    |   comparasion
    |   NAME '(' (value (',' value)*)? ')'
    |   '(' boolExpr ')';

AND         : 'and' ;
OR          : 'or' ;
NOT         : '!' ;

ifStatement: 'if' '(' boolExpr ')' '{' line* '}' elifStatement* elseStatement?;

elifStatement:  'elif' '(' boolExpr ')' '{' line* '}';

elseStatement:  'else' '{' line* '}';

whileStatement: 'while' '(' boolExpr ')' '{' line* '}';

comparasion: expr operator expr;

forStatement:   'for' '(' type ':' NAME '=' expr ';' boolExpr ';' NAME '=' expr ')' '{' line* '}';

operator: '=='
    | '>'
    | '>='
    | '<'
    | '<='
    | '!=';

assign: ('^')* NAME '=' value ';';

lambdaExpr: NAME '=>' value;

BlockComment: '/*' .*? '*/' -> channel(HIDDEN);

LineComment: '//' ~[\r\n]* -> channel(HIDDEN);

//Terminale
INT: [0-9]+ ;
DOUBLE: [0-9]+'.'[0-9]+;
NAME: [a-zA-Z][a-zA-Z0-9]*;
TEXT: '"' ~'"'* '"'; // Ciąg znaków w cudzysłowie
WS: [ \t\r\n]+ -> skip ;