'''
Count the frequency of each number
nums = [1, 2, 2, 3, 3, 3, 4]
'''

nums = [1, 2, 2, 3, 3, 3, 4]
output = {}

for num in nums:
    if num in output:
        output[num] += 1
    else:
        output[num] = 1

print(output)