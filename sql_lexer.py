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

import json
import ply.lex
import re

class SqlIllegalCharacter(Exception):
    def __init__(self, char):
        self.char = char
    def __str__(self):
        return "Encountered illegal character in Argo/SQL statement: '" + self.char + "'"

class SqlMalformedJSON(Exception):
    def __init__(self, json_str):
        self.json_str = json_str
    def __str__(self):
        return "Encountered malformed JSON in Argo/SQL statement:\n" + self.json_str

reserved = {
    'and':    'AND',
    'any':    'ANY',
    'delete': 'DELETE',
    'false':  'FALSE',
    'from':   'FROM',
    'insert': 'INSERT',
    'copy':   'COPY',
    'into':   'INTO',
    'like':   'LIKE',
    'not':    'NOT',
    'object': 'OBJECT',
    'or':     'OR',
    'select': 'SELECT',
    'true':   'TRUE',
    'where':  'WHERE'
}

tokens = [
    'STAR',
    'EQ',
    'NEQ',
    'LT',
    'GT',
    'LEQ',
    'GEQ',
    'PAREN_LEFT',
    'PAREN_RIGHT',
    'BRACKET_LEFT',
    'BRACKET_RIGHT',
    'COMMA',
    'DOT',
    'SEMICOLON',
    'QUOTED_STRING',
    'UINT',
    'FLOATVAL',
    'FILE',
    'NAME',
    'JSON'
] + list(reserved.values())

t_STAR          = r'\*'
t_EQ            = r'='
t_NEQ           = r'!='
t_LT            = r'<'
t_GT            = r'>'
t_LEQ           = r'<='
t_GEQ           = r'>='
t_PAREN_LEFT    = r'\('
t_PAREN_RIGHT   = r'\)'
t_BRACKET_LEFT  = r'\['
t_BRACKET_RIGHT = r'\]'
t_COMMA         = r','
t_DOT           = r'\.'
t_SEMICOLON     = r';'

def t_QUOTED_STRING(t):
    r'"([^"\n]|(\\"))*"'
    t.value = t.value[1:-1]
    return t

def t_FLOATVAL(t):
    r'[+\-]?[0-9]+(\.[0-9]+)?(e[+\-]?[0-9]+)?'
    if (re.search(r'[+\-\.e]', t.value)):
        t.value = float(t.value)
    else:
        t.value = int(t.value)
        t.type = 'UINT'
    return t

def t_NAME(t):
    r'[A-Za-z][A-Za-z0-9_]*'
    t.type = reserved.get(t.value.lower(), 'NAME')
    return t

def t_FILE(t):
    r'[A-Za-z/][A-Za-z0-9_/]*'
    t.type = reserved.get(t.value.lower(), 'FILE')
    return t

def t_JSON(t):
    r'\{.*\}'
    try:
        t.value = json.loads(t.value)
        return t
    except:
        raise SqlMalformedJSON(t.value)

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'

def t_error(t):
    t.lexer.skip(1)
    raise SqlIllegalCharacter(t.value[0])

lexer = ply.lex.lex()

