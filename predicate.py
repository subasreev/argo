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

def negate_comparison(comparison):
    if comparison == "=":
        return "!="
    elif comparison == "!=":
        return "="
    elif comparison == "<":
        return ">="
    elif comparison == "<=":
        return ">"
    elif comparison == ">":
        return "<="
    elif comparison == ">=":
        return "<"
    elif comparison == "LIKE":
        return "NOT LIKE"
    elif comparison == "NOT LIKE":
        return "LIKE"

def reverse_comparison(comparison):
    if comparison == "<":
        return ">"
    elif comparison == "<=":
        return ">="
    elif comparison == ">":
        return "<"
    elif comparison == ">=":
        return "<="
    else:
        return comparison


# KeyMatcher Interface: objects shall have properties:
#     - sql: SQL query text
#     - params: List of parameters to SQL query

class ExactKeyMatcher(object):
    def __init__(self, key):
        self.sql = "keystr = %s"
        self.params = [key]

class ArrayKeyMatcher(object):
    def __init__(self, array_key):
        self.sql = "keystr SIMILAR TO %s"
        self.params = [array_key + "\\[[0123456789]+\\]"]

# ValueMatcher Interface: objects shall have properties:
#     - sql: SQL query text
#     - params: List of parameters to SQL query
#     - argo3_table_suffix: Suffix of table for matched values in Argo/3
# And a method:
#     - get_negated_version(): Get the opposite of the ValueMatcher

class StringValueMatcher(object):
    def __init__(self, comparison, literal_value):
        self.comparison = comparison
        self.literal_value = literal_value
        self.sql = "valstr " + self.comparison + " %s"
        self.params = [self.literal_value]
        self.argo3_table_suffix = "_str"
    def get_negated_version(self):
        return StringValueMatcher(negate_comparison(self.comparison), self.literal_value)

class NumericValueMatcher(object):
    def __init__(self, comparison, literal_value):
        self.comparison = comparison
        self.literal_value = literal_value
        self.sql = "valnum " + self.comparison + " %s"
        self.params = [self.literal_value]
        self.argo3_table_suffix = "_num"
    def get_negated_version(self):
        return NumericValueMatcher(negate_comparison(self.comparison), self.literal_value)

class BooleanValueMatcher(object):
    def __init__(self, comparison, literal_value):
        self.comparison = comparison
        self.literal_value = literal_value
        self.sql = "valbool " + self.comparison + " %s"
        self.params = [self.literal_value]
        self.argo3_table_suffix = "_bool"
    def get_negated_version(self):
        return BooleanValueMatcher(negate_comparison(self.comparison), self.literal_value)


# Predicate Interface: objects shall have properties:
#     - params: List of parameters to SQL query
# And methods:
#     - set_collection_name(collection_name): Set the collection_name for the
#       Predicate and all children.
#     - get_negated_version(): Get the oppposite of the Predicate.
#     - get_argo1_sql(): Generate full SQL query text for Argo/1
#     - get_argo3_sql(): Generate full SQL query text for Argo/3

class SimplePredicate(object):
    def __init__(self, collection_name, keymatcher, valuematcher):
        self.collection_name = collection_name
        self.keymatcher = keymatcher
        self.valuematcher = valuematcher
        self.params = self.keymatcher.params
        self.params.extend(self.valuematcher.params)
    def set_collection_name(self, collection_name):
        self.collection_name = collection_name
    def get_negated_version(self):
        return SimplePredicate(self.collection_name,
                               self.keymatcher,
                               self.valuematcher.get_negated_version())
    def get_argo1_sql(self):
        return ("SELECT DISTINCT objid FROM argo_" + self.collection_name + "_data WHERE "
                + "(" + self.keymatcher.sql + ") AND (" + self.valuematcher.sql + ")")
    def get_argo3_sql(self):
        return ("SELECT DISTINCT objid FROM argo_" + self.collection_name
                + self.valuematcher.argo3_table_suffix + " WHERE " + "(" + self.keymatcher.sql
                + ") AND (" + self.valuematcher.sql + ")")

# Common functionality for DisjunctionPredicate and ConjunctionPredicate.
class TreePredicate(object):
    def __init__(self, collection_name, children = []):
        self.collection_name = collection_name
        self.children = children
        self.params = []
        for child in self.children:
            self.params.extend(child.params)
    def set_collection_name(self, collection_name):
        self.collection_name = collection_name
        for child in self.children:
            child.set_collection_name(collection_name)
    def add_child(self, child):
        self.children.append(child)
        self.params.extend(child.params)
    def get_argo1_sql(self):
        query_sql = "("
        for idx, child in enumerate(self.children):
            query_sql = query_sql + child.get_argo1_sql()
            if (idx == len(self.children) - 1):
                query_sql = query_sql + ")"
            else:
                query_sql = query_sql + ") " + self.combiner_word + " ("
        return query_sql
    def get_argo3_sql(self):
        query_sql = "("
        for idx, child in enumerate(self.children):
            query_sql = query_sql + child.get_argo3_sql()
            if (idx == len(self.children) - 1):
                query_sql = query_sql + ")"
            else:
                query_sql = query_sql + ") " + self.combiner_word + " ("
        return query_sql

class DisjunctionPredicate(TreePredicate):
    def __init__(self, collection_name, children = []):
        super(DisjunctionPredicate, self).__init__(collection_name, children)
        self.combiner_word = "UNION"
    def get_negated_version(self):
        negated_children = []
        for child in self.children:
            negated_children.append(child.get_negated_version())
        return ConjunctionPredicate(self.collection_name, negated_children)

class ConjunctionPredicate(TreePredicate):
    def __init__(self, collection_name, children = []):
        super(ConjunctionPredicate, self).__init__(collection_name, children)
        self.combiner_word = "INTERSECT"
    def get_negated_version(self):
        negated_children = []
        for child in self.children:
            negated_children.append(child.get_negated_version())
        return DisjunctionPredicate(self.collection_name, negated_children)

class NegationPredicate(object):
    def __init__(self, collection_name, child):
        self.collection_name = collection_name
        self.child = child
        self.negated_child = child.get_negated_version()
        self.params = self.negated_child.params
    def set_collection_name(self, collection_name):
        self.collection_name = collection_name
        self.child.set_collection_name(collection_name)
        self.negated_child.set_collection_name(collection_name)
    def get_negated_version(self):
        return self.child
    def get_argo1_sql(self):
        return self.negated_child.get_argo1_sql()
    def get_argo3_sql(self):
        return self.negated_child.get_argo3_sql()
