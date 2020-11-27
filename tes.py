class solution:

    def solution(data, n): 
        #check element
        lim = 99
        if any(i > lim for i in data):
            print("data element must less than 100")
            return
        for i in set(data):
            if data.count(i) > n:
                while i in data:
                    data.remove(i)
        print(*data, sep=",")

solution.solution([1, 2, 2, 3, 3, 3, 4, 5, 5], 1)