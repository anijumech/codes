'''
I need you to write a Python function that takes in a list of one or more integers and returns them rearranged into a staircase, if possible, or False otherwise. A staircase is a list of lists where list 0 has length 1, and every list i+1 is one item longer than list i. The order of the elements in the staircase doesn’t matter.

Here are some input/output examples that show what I mean:

Input: [1, 2, 3, 4, 5, 6]

Output: [[1], [2, 3], [4, 5, 6]]

Input: [1, 2, 3, 4, 5, 6, 7]

Output: False

In the example [1, 2, 3, 4, 5, 6, 7], the list of lists only has one element in its fourth list:

[[1], [2, 3], [4, 5, 6], [7]]

index -> 0, 1, 2, 3, 4, 5
step -> 1, 2, 3, 4, 5, 6
exindex -> 0, 1, 3, 6, 10, 15

That is NOT equal to the length of the previous list plus one. The last list would have to have four elements to be a valid staircase.
'''

input = [1, 2, 3, 4, 5, 6, 9, 10, 44, 8]
step = 1
output = []

while len(input) != 0:
    if len(input) >= step:
        output.append(input[0:step])
        input = input[step:]
        step += 1
    else:
        output = False
        break

print(output)