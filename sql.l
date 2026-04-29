%{
#include "sql.tab.h"
#include <string.h>
%}

%option yylineno
%option caseless

%%

"SELECT"    { return SELECT; }
"FROM"      { return FROM; }
"WHERE"     { return WHERE; }
"AND"       { return AND; }
"OR"        { return OR; }
"INSERT"    { return INSERT; }
"INTO"      { return INTO; }
"VALUES"    { return VALUES; }
"UPDATE"    { return UPDATE; }
"SET"       { return SET; }
"DELETE"    { return DELETE; }
"CREATE"    { return CREATE; }
"TABLE"     { return TABLE; }
"DATABASE"  { return DATABASE; }
"DROP"      { return DROP; }
"ALTER"     { return ALTER; }
"ADD"       { return ADD; }
"COLUMN"    { return COLUMN; }
"INT"       { return INT; }
"VARCHAR"   { return VARCHAR; }

"GRANT"     { return GRANT; }
"REVOKE"    { return REVOKE; }
"ON"        { return ON; }
"TO"        { return TO; }
"ALL"       { return ALL; }

"*"         { return STAR; }
"="         { return EQ; }
","         { return COMMA; }
"("         { return LPAREN; }
")"         { return RPAREN; }
";"         { return SEMI; }

[a-zA-Z][a-zA-Z0-9_]* { yylval.str = strdup(yytext); return ID; }
[0-9]+                { yylval.num = atoi(yytext); return NUM; }
\'[^\']*\'            { yylval.str = strdup(yytext); return STRING; }

[ \t\r\n]+            ; 

.                     { fprintf(stderr, "[ERROR]|%d|Invalid character|%s\n", yylineno, yytext); }

%%

int yywrap() {
    return 1;
}
