
def min_max_distance(n, k, L):
    def can_place(d):
        count = 0
        for length in L:
            count += (length - 1) // d
        return count <= k

    left, right = 1, max(L)

    while left < right:
        mid = (left + right) // 2
        if can_place(mid):
            right = mid
        else:
            left = mid + 1

    result = []
    for length in L:
        parts = max(1, (length + left - 1) // left)
        for _ in range(parts - 1):
            result.append(length // parts)
        result.append(length - (length // parts) * (parts - 1))

    return result


if __name__ == "__main__":
    n = 3
    k = 3
    L = [10, 20, 30]

    print("Новое распределение расстояний между банкоматами:")
    print(min_max_distance(n, k, L))
