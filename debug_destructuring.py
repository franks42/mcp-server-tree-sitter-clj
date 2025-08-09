#!/usr/bin/env python3
"""Debug destructuring pattern detection"""

import re

# Simple test code
simple_code = """(defn test-func [{:keys [a b]}]
  (println a b))"""

print("Testing simple destructuring pattern detection")
print(f"Code: {repr(simple_code)}")

# Test the regex pattern
pattern_regex = r"\(\s*defn-?\s+[\w-]+\s+\[([^\]]+)\]"
matches = re.finditer(pattern_regex, simple_code)

print("\nMatches found:")
for match in matches:
    print(f"  Full match: {repr(match.group(0))}")
    print(f"  Binding text: {repr(match.group(1))}")

    # Test the map destructuring pattern
    binding_text = match.group(1)
    map_destructuring = re.findall(r"\{[^}]*:keys\s+\[([^\]]+)\][^}]*\}", binding_text)
    print(f"  Map destructuring found: {map_destructuring}")

print("\nTesting more complex case:")
complex_code = """(defn complex [{:keys [name age] :as user} [x y]]
  (println name age x y))"""

print(f"Code: {repr(complex_code)}")
matches = re.finditer(pattern_regex, complex_code)

for match in matches:
    print(f"  Full match: {repr(match.group(0))}")
    print(f"  Binding text: {repr(match.group(1))}")
