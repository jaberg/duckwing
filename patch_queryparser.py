from pyparsing import *

LBRK = Suppress("[")
RBRK = Suppress("]")

number = Regex(r"[+-]?\d+(:?\.\d*)?(:?[eE][+-]?\d+)?")
number.add_parse_action(lambda t: float(t[0]))  # convert to float
string_ = quotedString.add_parse_action(lambda t: t[0][1:-1])  # remove quotes

EntityName = Word(alphanums + "_")
# ExcludeEntityName = Word(alphanums + '_!')
ExcludeEntityName = Regex(r"[!][\w]+")
AttribName = Word(alphanums + "_")
Relation = one_of(["==", "!=", "<", "<=", ">", ">=", "?", "!?"])

AttribValue = string_ | number
AttribQuery = Group(AttribName + Relation + AttribValue)
EntityNames = Group(
    (Literal("*") + ZeroOrMore(ExcludeEntityName)) | OneOrMore(EntityName)
).set_results_name("EntityQuery")

InfixBoolQuery = infix_notation(
    AttribQuery,
    (
        ("!", 1, opAssoc.RIGHT),
        ("&", 2, opAssoc.LEFT),
        ("|", 2, opAssoc.LEFT),
    ),
).set_results_name("AttribQuery")

AttribQueryOptions = Literal("i").set_results_name("AttribQueryOptions")

EntityQueryParser = EntityNames + Optional(
    LBRK + InfixBoolQuery + RBRK + Optional(AttribQueryOptions)
)
