'''
Problem #4 — Valid Parentheses

Given a string s containing only:

( ) { } [ ]

determine whether the input string is valid.

A string is valid if:

Every opening bracket has a corresponding closing bracket.
Brackets close in the correct order.
Every closing bracket matches the most recent unmatched opening bracket.
'''

# input = "([{}])"
# input = "([)]"
# input = "({[]})[({})]{{[()]}}(([[{{()}}]]))[{({[]})}]({[({})]})"
# input = "({[]})[({})]{{[()]}}(([[{{()}}]]))[{({[]})}]({[({})])}"
input = "]{}[]"
decision = True
lifoArray = []

for item in input:
    if item == '(' or item == '{' or item == '[':
        lifoArray.append(item)
    elif len(lifoArray) != 0 and ((item == ')' and lifoArray[-1] == '(') or (item == '}' and lifoArray[-1] == '{') or (item == ']' and lifoArray[-1] == '[')):
        lifoArray.pop(-1)
    else:
        decision = False
    print(lifoArray)

print(decision)

'''
This solution leads to both Time and Space Complexity as O(n)
'''




