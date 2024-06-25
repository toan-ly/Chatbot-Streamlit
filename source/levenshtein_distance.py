import streamlit as st
from utils.timing import timeit
import os

def levenshtein_distance_dp(token1: str, token2: str) -> int:
    distances = [[0]*(len(token2)+1) for _ in range(len(token1)+1)]

    for t1 in range(len(token1) + 1):
        distances[t1][0] = t1

    for t2 in range(len(token2) + 1):
        distances[0][t2] = t2

    a = 0
    b = 0
    c = 0

    for t1 in range(1, len(token1) + 1):
        for t2 in range(1, len(token2) + 1):
            if (token1[t1-1] == token2[t2-1]):
                distances[t1][t2] = distances[t1 - 1][t2 - 1]
            else:
                a = distances[t1][t2 - 1]
                b = distances[t1 - 1][t2]
                c = distances[t1 - 1][t2 - 1]

                if (a <= b and a <= c):
                    distances[t1][t2] = a + 1
                elif (b <= a and b <= c):
                    distances[t1][t2] = b + 1
                else:
                    distances[t1][t2] = c + 1

    return distances[len(token1)][len(token2)]

def levenshtein_distance_bfs(token1: str, token2: str) -> int:
    m, n = len(token1), len(token2)

    to_visit = [(0, 0)] # Initial location
    visited = set()
    dist = 0

    while to_visit:
        next_lvl = []
        while to_visit:
            row, col = to_visit.pop()

            # Skip already visited locations
            if (row, col) in visited:
                continue

            # Move forward in both tokens as long as characters match
            while row < m and col < n and token1[row] == token2[col]:
                row += 1 
                col += 1
            
            # End of both tokens
            if row == m and col == n:
                return dist

            # Add possible locations to the next level
            if (row, col + 1) not in visited:
                next_lvl.append((row, col + 1)) # Insertion
            if (row + 1, col) not in visited:
                next_lvl.append((row + 1, col)) # Deletion
            if (row + 1, col + 1) not in visited:
                next_lvl.append((row + 1, col + 1)) # Substitution
                
            visited.add((row, col)) # Mark current location as visited

        dist += 1
        to_visit = next_lvl # Update queue with next level

def load_vocab(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    words = sorted(set([line.strip().lower() for line in lines]))
    return words

@timeit
def compute_distances(word, vocabs, method='bfs'):
    leven_distances = dict()
    for vocab in vocabs:
        if method == 'bfs':
            leven_distances[vocab] = levenshtein_distance_bfs(word, vocab) 
        elif method == 'dp':
            leven_distances[vocab] = levenshtein_distance_dp(word, vocab)
    return leven_distances

def main():
    BASE_DIR = os.path.join(os.path.dirname(__file__))
    vocabs_file_path = os.path.join(BASE_DIR, 'data', 'vocab.txt')
    vocabs = load_vocab(vocabs_file_path)

    st.title("Word Correction using Levenshtein Distance")
    word = st.text_input('Word:')

    if st.button("Compute"):
        # compute levenshtein distance
        leven_distances = compute_distances(word, vocabs, 'dp')
        
        # sorted by distance
        sorted_distences = dict(sorted(leven_distances.items(), key=lambda item: item[1]))
        correct_word = list(sorted_distences.keys())[0]
        st.write('Correct word: ', correct_word)

        col1, col2 = st.columns(2)
        col1.write('Vocabulary:')
        col1.write(vocabs)
        
        col2.write('Distances:')
        col2.write(sorted_distences)

if __name__ == "__main__":
    main()