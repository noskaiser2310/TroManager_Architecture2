import re

with open('tests/e2e_stress_test.py', encoding='utf-8') as f:
    content = f.read()

# Fix trailing ) after f-string closing quotes
content = re.sub(r'\}"\)', r'}"', content)

with open('tests/e2e_stress_test.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed')

# Verify syntax
import ast
try:
    ast.parse(content)
    print('Syntax OK')
except SyntaxError as e:
    print(f'Syntax error: {e}')
