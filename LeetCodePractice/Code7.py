'''
Next problem: Group Anagrams

This will bring us back to the HashMap pattern, but with a more challenging application.

Given:

strs = ["eat", "tea", "tan", "ate", "nat", "bat"]

return:

[
    ["eat", "tea", "ate"],
    ["tan", "nat"],
    ["bat"]
]

Challenge: Try to solve it using a dictionary. Don't use a nested comparison of every string against every other string.

'''
strs = ["eat", "tea", "tan", "ate", "nat", "bat"]
hmap = {}
for item in strs:
    sorteditem = "".join(sorted(item))
    if sorteditem not in hmap:
        hmap[sorteditem] = [item]
    else:
        hmap[sorteditem].append(item)

print(hmap.values())

'''
This takes the advantage of sorting and same keys in dictionary are not allowed.
'''


