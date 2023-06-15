def build_array(string1, string2):
    M = []
    for i in range(len(string1) + 1):
        for j in range(len(string2) + 1):
            if j == 0:
                M.append([i])
            elif i == 0:
                M[i].append(j)
            else:
                M[i].append(0)
    for i in range(1, len(string1) + 1):
        for j in range(1, len(string2) + 1):
            if string1[i - 1] == string2[j - 1]:
                M[i][j] = M[i - 1][j - 1]
            else:
                M[i][j] = min(M[i - 1][j], M[i][j - 1], M[i - 1][j - 1]) + 1
    return M

def levenschtein_distance(string1, string2):
    return build_array(string1, string2)[len(string1)][len(string2)]

def filter_by_word(searched, A):
    res = []
    for i in range(10):
        res.append([])
    for row in A:
        best = 9
        if len(searched.split()) > 1:
            best = min(levenschtein_distance(searched.lower(), row.name[:len(searched)].lower()), best)
        else:
            for word in row.name.split():
                best = min(levenschtein_distance(searched.lower(), word[:len(searched)].lower()), best)
        res[best].append(row)
    result = []
    for i in range(len(res)):
        for j in range(len(res[i])):
            result.append(res[i][j])
    return result