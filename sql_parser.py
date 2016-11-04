#!/usr/bin/env python2

#   Copyright (c) 2011-2013, Craig Chasseur.
#
#   This file is part of Argo.
#
#   Argo is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Argo is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Argo.  If not, see <http://www.gnu.org/licenses/>.

import ply.yacc

from sql_lexer import tokens
import predicate
import projector
import query

class SqlSyntaxError(Exception):
    def __str__(self):
        return "Encountered syntax error in Argo/SQL" 

def p_command(p):
    '''command : sql_statement
               | sql_statement SEMICOLON'''
    p[0] = p[1]

def p_sql_statement(p):
    '''sql_statement : select_statement
                     | insert_statement
                     | copy_statement
                     | delete_statement'''
    p[0] = p[1]

def p_select_statement(p):
    '''select_statement : SELECT projection FROM NAME WHERE or_predicate
                        | SELECT projection FROM NAME'''
    if (len(p) == 5):
        p[0] = query.SelectQuery(p[4], p[2])
    else:
        p[0] = query.SelectQuery(p[4], p[2], p[6])

def p_insert_statement(p):
    '''insert_statement : INSERT INTO NAME OBJECT JSON'''
    p[0] = query.InsertQuery(p[3], p[5])

def p_copy_statement(p):
    '''copy_statement : COPY NAME FROM FILE'''
    p[0] = query.CopyQuery(p[2], p[4])


def p_delete_statement(p):
    '''delete_statement : DELETE FROM NAME WHERE or_predicate
                        | DELETE FROM NAME'''
    if (len(p) == 4):
        p[0] = query.DeleteQuery(p[3])
    else:
        p[0] = query.DeleteQuery(p[3], p[5])

def p_projection(p):
    '''projection : STAR
                  | project_list'''
    if (p[1] == "*"):
        p[0] = projector.StarProjector("placeholder")
    else:
        p[0] = p[1]

def p_project_list(p):
    '''project_list : project_list COMMA attribute_key
                    | attribute_key'''
    if (len(p) == 4):
        p[0] = p[1]
        p[0].add_key(p[3])
    else:
        p[0] = projector.ListProjector("placeholder")
        p[0].add_key(p[1])

def p_attribute_key(p):
    '''attribute_key : attribute_key DOT NAME
                     | attribute_key BRACKET_LEFT UINT BRACKET_RIGHT
                     | NAME'''
    if (len(p) == 2):
        p[0] = p[1]
    elif (len(p) == 5):
        p[0] = p[1] + "[" + str(p[3]) + "]"
    else:
        p[0] = p[1] + "." + p[3]

def p_bool_comparison_op(p):
    '''bool_comparison_op : EQ
                          | NEQ'''
    p[0] = p[1]

def p_num_comparison_op(p):
    '''num_comparison_op : bool_comparison_op
                         | LT
                         | LEQ
                         | GT
                         | GEQ'''
    p[0] = p[1]

def p_str_comparison_op(p):
    '''str_comparison_op : num_comparison_op
                         | LIKE
                         | NOT LIKE'''
    if (len(p) == 3):
        p[0] = "NOT LIKE"
    else:
        p[0] = p[1]

		
def p_bool_val(p):
    '''bool_val : TRUE
                | FALSE'''
    if (p[1].lower() == "true"):
        p[0] = True
    else:
        p[0] = False

def p_num_val(p):
    '''num_val : FLOATVAL
               | UINT'''
    p[0] = float(p[1])

def p_str_val(p):
    '''str_val : QUOTED_STRING'''
    p[0] = p[1]


def p_simple_bool_predicate(p):
    '''simple_bool_predicate : attribute_key bool_comparison_op bool_val
                             | bool_val bool_comparison_op attribute_key
                             | ANY attribute_key bool_comparison_op bool_val
                             | bool_val bool_comparison_op ANY attribute_key'''
    if (len(p) == 4):
        if (isinstance(p[1], bool)):
            p[0] = predicate.SimplePredicate("placeholder",
                                             predicate.ExactKeyMatcher(p[3]),
                                             predicate.BooleanValueMatcher(
                                                 predicate.reverse_comparison(p[2]), p[1]))
        else:
            p[0] = predicate.SimplePredicate("placeholder",
                                             predicate.ExactKeyMatcher(p[1]),
                                             predicate.BooleanValueMatcher(p[2], p[3]))
    else:
        if (isinstance(p[1], bool)):
            p[0] = predicate.SimplePredicate("placeholder",
                                             predicate.ArrayKeyMatcher(p[4]),
                                             predicate.BooleanValueMatcher(
                                                 predicate.reverse_comparison(p[2]), p[1]))
        else:
            p[0] = predicate.SimplePredicate("placeholder",
                                             predicate.ArrayKeyMatcher(p[2]),
                                             predicate.BooleanValueMatcher(p[3], p[4]))

def p_simple_num_predicate(p):
    '''simple_num_predicate : attribute_key num_comparison_op num_val
                              | num_val num_comparison_op attribute_key
                              | ANY attribute_key num_comparison_op num_val
                              | num_val num_comparison_op ANY attribute_key'''
    if (len(p) == 4):
        if (isinstance(p[1], float)):
            p[0] = predicate.SimplePredicate("placeholder",
                                             predicate.ExactKeyMatcher(p[3]),
                                             predicate.NumericValueMatcher(
                                                 predicate.reverse_comparison(p[2]), p[1]))
        else:
            p[0] = predicate.SimplePredicate("placeholder",
                                             predicate.ExactKeyMatcher(p[1]),
                                             predicate.NumericValueMatcher(p[2], p[3]))
    else:
        if (isinstance(p[1], float)):
            p[0] = predicate.SimplePredicate("placeholder",
                                             predicate.ArrayKeyMatcher(p[4]),
                                             predicate.NumericValueMatcher(
                                                 predicate.reverse_comparison(p[2]), p[1]))
        else:
            p[0] = predicate.SimplePredicate("placeholder",
                                             predicate.ArrayKeyMatcher(p[2]),
                                             predicate.NumericValueMatcher(p[3], p[4]))


def p_simple_str_predicate_left(p):
    '''simple_str_predicate_left : attribute_key str_comparison_op str_val
                                 | ANY attribute_key str_comparison_op str_val'''
    if (len(p) == 4):
        p[0] = predicate.SimplePredicate("placeholder",
                                         predicate.ExactKeyMatcher(p[1]),
                                         predicate.StringValueMatcher(p[2], p[3]))
    else:
        p[0] = predicate.SimplePredicate("placeholder",
                                         predicate.ArrayKeyMatcher(p[2]),
                                         predicate.StringValueMatcher(p[3], p[4]))

def p_simple_str_predicate_right(p):
    '''simple_str_predicate_right : str_val str_comparison_op attribute_key
                                  | str_val str_comparison_op ANY attribute_key'''
    if (len(p) == 4):
        p[0] = predicate.SimplePredicate("placeholder",
                                         predicate.ExactKeyMatcher(p[3]),
                                         predicate.StringValueMatcher(
                                             predicate.reverse_comparison(p[2]), p[1]))
    else:
        p[0] = predicate.SimplePredicate("placeholder",
                                         predicate.ArrayKeyMatcher(p[4]),
                                         predicate.StringValueMatcher(
                                             predicate.reverse_comparison(p[2]), p[1]))

def p_simple_str_predicate(p):
    '''simple_str_predicate : simple_str_predicate_left
                            | simple_str_predicate_right'''
    p[0] = p[1]

def p_simple_predicate(p):
    '''simple_predicate : simple_bool_predicate
                        | simple_num_predicate
                        | simple_str_predicate'''
    p[0] = p[1]

def p_predicate_base(p):
    '''predicate_base : simple_predicate
                      | PAREN_LEFT or_predicate PAREN_RIGHT'''
    if (len(p) == 2):
        p[0] = p[1]
    else:
        p[0] = p[2]

def p_not_predicate(p):
    '''not_predicate : NOT predicate_base
                     | predicate_base'''
    if (len(p) == 2):
        p[0] = p[1]
    else:
        p[0] = predicate.NegationPredicate("placeholder", p[2])

def p_and_predicate(p):
    '''and_predicate : and_predicate AND not_predicate
                     | not_predicate'''
    if (len(p) == 2):
        p[0] = p[1]
    else:
        if isinstance(p[1], predicate.ConjunctionPredicate):
            p[1].add_child(p[3])
            p[0] = p[1]
        else:
            p[0] = predicate.ConjunctionPredicate("placeholder", [p[1], p[3]])

def p_or_predicate(p):
    '''or_predicate : or_predicate OR and_predicate
                    | and_predicate'''
    if (len(p) == 2):
        p[0] = p[1]
    else:
        if isinstance(p[1], predicate.DisjunctionPredicate):
            p[1].add_child(p[3])
            p[0] = p[1]
        else:
            p[0] = predicate.DisjunctionPredicate("placeholder", [p[1], p[3]])

def p_error(p):
    raise SqlSyntaxError()

parser = ply.yacc.yacc()
