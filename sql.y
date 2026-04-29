%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

extern int yylineno;
extern char *yytext;
void yyerror(const char *s);
extern int yylex();

int levenshtein(const char *s1, const char *s2) {
    int len1 = strlen(s1), len2 = strlen(s2);
    int matrix[len1 + 1][len2 + 1];
    for (int i = 0; i <= len1; i++) matrix[i][0] = i;
    for (int j = 0; j <= len2; j++) matrix[0][j] = j;
    for (int i = 1; i <= len1; i++) {
        for (int j = 1; j <= len2; j++) {
            int cost = (toupper(s1[i-1]) == toupper(s2[j-1])) ? 0 : 1;
            int a = matrix[i-1][j] + 1;
            int b = matrix[i][j-1] + 1;
            int c = matrix[i-1][j-1] + cost;
            matrix[i][j] = (a < b) ? (a < c ? a : c) : (b < c ? b : c);
        }
    }
    return matrix[len1][len2];
}

const char* find_closest(const char* input) {
    const char* valid[] = {"SELECT", "UPDATE", "INSERT", "DELETE", "ALL", "GRANT", "REVOKE"};
    int min_dist = 99;
    const char* best = valid[0];
    for (int i = 0; i < 7; i++) {
        int d = levenshtein(input, valid[i]);
        if (d < min_dist) {
            min_dist = d;
            best = valid[i];
        }
    }
    return best;
}
%}

%define parse.error verbose
%union { char *str; int num; }

%token SELECT FROM WHERE AND OR INSERT INTO VALUES UPDATE SET DELETE
%token CREATE TABLE DATABASE DROP ALTER ADD COLUMN INT VARCHAR
%token GRANT REVOKE ON TO ALL
%token STAR EQ COMMA LPAREN RPAREN SEMI
%token <str> ID STRING
%token <num> NUM

%left OR AND
%left EQ

%%

program: statements ;
statements: statement | statements statement ;
statement: query SEMI | error SEMI { yyerrok; } ;

query: select_stmt | insert_stmt | update_stmt | delete_stmt 
     | create_table_stmt | create_db_stmt | drop_table_stmt | drop_db_stmt | alter_table_stmt
     | grant_stmt | revoke_stmt ;

grant_stmt: GRANT privilege ON ID TO ID ;
revoke_stmt: REVOKE privilege ON ID FROM ID ;

privilege
    : ALL | SELECT | INSERT | UPDATE | DELETE 
    | ID { 
        char msg[128];
        const char* suggestion = find_closest($1);
        sprintf(msg, "Invalid privilege '%s'. Did you mean %s?", $1, suggestion);
        yyerror(msg);
        YYERROR;
    }
    ;

select_stmt : SELECT select_list FROM table_list where_clause ;
select_list : STAR | column_list ;
column_list : ID | column_list COMMA ID ;
table_list  : ID | table_list COMMA ID ;
where_clause : /* empty */ | WHERE condition_list ;
condition_list : condition | condition_list AND condition | condition_list OR condition ;
condition : ID EQ value ;
value : NUM | STRING | ID ;
insert_stmt : INSERT INTO ID LPAREN column_list RPAREN VALUES LPAREN value_list RPAREN | INSERT INTO ID VALUES LPAREN value_list RPAREN ;
value_list : value | value_list COMMA value ;
update_stmt : UPDATE ID SET update_list where_clause ;
update_list : ID EQ value | update_list COMMA ID EQ value ;
delete_stmt : DELETE FROM ID where_clause ;
create_table_stmt : CREATE TABLE ID LPAREN column_def_list RPAREN ;
column_def_list : column_def | column_def_list COMMA column_def ;
column_def : ID data_type ;
data_type : INT | VARCHAR LPAREN NUM RPAREN ;
create_db_stmt : CREATE DATABASE ID ;
drop_table_stmt : DROP TABLE ID ;
drop_db_stmt : DROP DATABASE ID ;
alter_table_stmt : ALTER TABLE ID ADD COLUMN ID data_type | ALTER TABLE ID DROP COLUMN ID ;

%%

void yyerror(const char *s) {
    fprintf(stderr, "[ERROR]|%d|%s|%s\n", yylineno, s, yytext);
}

int main() { return yyparse(); }
