from reader.program import Program

import tree_sitter_java as tsjava
from tree_sitter import Language, Parser

JLANG = Language(tsjava.language())
JLANG_PARSER = Parser(JLANG)

def get_int_literals(program: Program) -> set[int]:
    ints: set[int] = set()

    for file in program.files.values():
        tree = JLANG_PARSER.parse(bytes(file.source, "utf8"))
        query = JLANG.query("(decimal_integer_literal) @literal")
        res = query.captures(tree.root_node)
        literals = res["literal"] if "literal" in res else []
        for node in literals:
            ints.add(int(node.text))

    return ints
