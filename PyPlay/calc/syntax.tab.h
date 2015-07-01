/* A Bison parser, made by GNU Bison 2.3.  */

/* Skeleton interface for Bison's Yacc-like parsers in C

   Copyright (C) 1984, 1989, 1990, 2000, 2001, 2002, 2003, 2004, 2005, 2006
   Free Software Foundation, Inc.

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2, or (at your option)
   any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 51 Franklin Street, Fifth Floor,
   Boston, MA 02110-1301, USA.  */

/* As a special exception, you may create a larger work that contains
   part or all of the Bison parser skeleton and distribute that work
   under terms of your choice, so long as that work isn't itself a
   parser generator using the skeleton or a modified version thereof
   as a parser skeleton.  Alternatively, if you modify or redistribute
   the parser skeleton itself, you may (at your option) remove this
   special exception, which will cause the skeleton and the resulting
   Bison output files to be licensed under the GNU General Public
   License without this special exception.

   This special exception was added by the Free Software Foundation in
   version 2.2 of Bison.  */

/* Tokens.  */
#ifndef YYTOKENTYPE
# define YYTOKENTYPE
   /* Put the tokens into the symbol table, so that GDB and other debuggers
      know about them.  */
   enum yytokentype {
     lex_identifier = 258,
     lex_constant = 259,
     lex_endstmt = 260,
     lex_comma = 261,
     lex_oparen = 262,
     lex_cparen = 263,
     lex_obracket = 264,
     lex_cbracket = 265,
     lex_osqbracket = 266,
     lex_csqbracket = 267,
     lex_givenkwd = 268,
     lex_withkwd = 269,
     lex_inkwd = 270,
     lex_constantkwd = 271,
     lex_variablekwd = 272,
     lex_functionkwd = 273,
     lex_minus = 274,
     lex_plus = 275,
     lex_div = 276,
     lex_mul = 277,
     lex_pow = 278,
     NEG = 279,
     lex_equals = 280,
     lex_eq = 281,
     lex_gt = 282,
     lex_ge = 283,
     lex_le = 284,
     lex_lt = 285,
     lex_logical_or = 286,
     lex_logical_and = 287,
     lex_assign = 288
   };
#endif
/* Tokens.  */
#define lex_identifier 258
#define lex_constant 259
#define lex_endstmt 260
#define lex_comma 261
#define lex_oparen 262
#define lex_cparen 263
#define lex_obracket 264
#define lex_cbracket 265
#define lex_osqbracket 266
#define lex_csqbracket 267
#define lex_givenkwd 268
#define lex_withkwd 269
#define lex_inkwd 270
#define lex_constantkwd 271
#define lex_variablekwd 272
#define lex_functionkwd 273
#define lex_minus 274
#define lex_plus 275
#define lex_div 276
#define lex_mul 277
#define lex_pow 278
#define NEG 279
#define lex_equals 280
#define lex_eq 281
#define lex_gt 282
#define lex_ge 283
#define lex_le 284
#define lex_lt 285
#define lex_logical_or 286
#define lex_logical_and 287
#define lex_assign 288




#if ! defined YYSTYPE && ! defined YYSTYPE_IS_DECLARED
typedef int YYSTYPE;
# define yystype YYSTYPE /* obsolescent; will be withdrawn */
# define YYSTYPE_IS_DECLARED 1
# define YYSTYPE_IS_TRIVIAL 1
#endif

extern YYSTYPE yylval;

