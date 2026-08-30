arr = []
arrreversed = []
for i in range(1, 5000):
    arr.append(i)

arrreversed = arr[::-1]
arr.extend(arrreversed)
arr.append(50000)

print(arr)
