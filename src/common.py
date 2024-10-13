import Levenshtein


def find_close_strings(strings, threshold):
    """Finds and returns close strings, sorted by Levenshtein distance."""
    close_pairs = []
    n = len(strings)

    for i in range(n):
        for j in range(i + 1, n):
            dist = Levenshtein.distance(strings[i], strings[j])
            if dist <= threshold and dist > 0:
                close_pairs.append((strings[i], strings[j], dist))
    close_pairs.sort(key=lambda x: x[2])
    return close_pairs
