'''
Given an integer array nums, return True if any value appears at least twice in the array, and return False if every element is distinct.
'''

nums = [1,4,55,2,0,5,3,2,76]

storage = {}
finalResult = False

for index, num in enumerate(nums):
    if num in storage:
        finalResult = True
        print(finalResult)
        break
    
    storage[num] = index

if not finalResult:
    print(finalResult)


'''
Here, the space and time complexity both are O(n) i.e linear
'''