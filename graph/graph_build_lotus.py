import tree_sitter
import tree_sitter_lotus

# Create a parser
parser = tree_sitter.Parser()
language = tree_sitter.Language(tree_sitter_lotus.language())

parser.language = language

# Parse some LotusScript code
code = """
Option Public

Sub HelloWorld(name As String)
  Dim message As String
  message = "Hello, " & name & "!"
  Call PrintMessage(message)
End Sub
"""

tree = parser.parse(code.encode('utf-8'))
root = tree.root_node

# Explore the syntax tree
print(f"Root node type: {root.type}")
for child in root.children:
    print(f"  - {child.type}: {child.text.decode('utf-8')}")