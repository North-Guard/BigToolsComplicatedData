import json
import pickle
import sqlite3
import sys
from pathlib import Path
from time import time
import regex as re
from nested_re_search_method import task_re_pattern, nested_search

sys.setrecursionlimit(25000)

########################################################################################
# Loading data and connecting to databases

input_dir = Path("/dtu-compute", "dabai")

# Connect to article-database
connection_articles = sqlite3.connect(str(Path(input_dir, "Articles.db")))
cursor_articles = connection_articles.cursor()

# Largest article-id
cursor_articles.execute("SELECT Ident FROM articles ORDER BY Ident DESC LIMIT 1")
max_article_id = cursor_articles.fetchone()[0]

# Connect to word-database
connection_words = sqlite3.connect(str(Path(input_dir, "Wordbase.db")))
cursor_words = connection_words.cursor()

# Largest word-id
cursor_words.execute("SELECT Ident FROM words ORDER BY Ident DESC LIMIT 1")
max_word_id = cursor_words.fetchone()[0]

# Check if files have already been created
start = time()
word_search_path = Path(input_dir, "word_search")
if Path(word_search_path, "vocabulary.p").is_file():
    print("Loading files")
    vocabulary = pickle.load(Path(word_search_path, "vocabulary.p").open("rb"))
    massive_keys_string = pickle.load(Path(word_search_path, "massive_keys_string.p").open("rb"))
    key_index_list = pickle.load(Path(word_search_path, "key_index_list.p").open("rb"))
else:

    # Get all words and IDs
    cursor_words.execute("SELECT Ident, Word FROM words ORDER BY Ident")

    print("Creating vocabulary.")
    vocabulary = dict()
    fetch = cursor_words.fetchone()
    while fetch is not None:
        idx, word = fetch
        if idx % 1000000 == 0:
            print(f"{idx} / {max_word_id}")
        vocabulary[word] = idx
        fetch = cursor_words.fetchone()

    # Make massive key-string
    print("Concatenating keys")
    keys = list(vocabulary.keys())
    massive_keys_string = "£".join(keys)

    # Determine indices of keys
    print("Making key-indices")
    key_lengths = [len(key) for key in keys]
    key_index_list = [val
                      for idx, length in enumerate(key_lengths)
                      for val in [idx] * (length + 1)]

    # Storage
    print("Storing files for word-search")
    pickle.dump(vocabulary, Path(word_search_path, "vocabulary.p").open("wb"))
    pickle.dump(massive_keys_string, Path(word_search_path, "massive_keys_string.p").open("wb"))
    pickle.dump(key_index_list, Path(word_search_path, "key_index_list.p").open("wb"))

end = time()
print(f"Created / Loaded files in {end - start:.2f}s")

########################################################################################
###############################################################################################################
########################################################################################
#
# Cat search
#
print("\n\n" + "-" * 80)
print("Cat Search")
print("-" * 80)
start = time()

# Get cat-article
cat_article_id = pickle.load(Path(input_dir, "cat_list.p").open("rb"))[0]
cursor_articles.execute("SELECT article FROM articles WHERE ident == {}".format(cat_article_id))
article = cursor_articles.fetchone()[0]

# Queries
queries = [
    ['cat', (0, 10), 'are', (0, 10), 'to'],
    ['cat', (0, 100), 'anatomy'],
    ['china', (30, 150), 'washington'],
    ['english', (0, 200), 'cat'],
    ['kitten', (15, 85), 'cat', (0, 100), 'sire', (0, 200), 'oxford']
]

# Make queries
for query in queries:
    query_start = time()
    print(f"\nStarting query for {query}")
    result = nested_search(query, article)
    print("Got 1 results and {} matches in {:.2f}s".format(len(result), time() - query_start))

print(f"\nAll patterns in cat-article matched in {time() - start:.2f}s")

########################################################################################
###############################################################################################################
########################################################################################
#
# 'A' search
#
print("\n\n" + "-" * 80)
print("'A' Search")
print("-" * 80)
start = time()

# Get 'a'-articles
a_article_ids = pickle.load(Path(input_dir, "a_articles.p").open("rb"))
cursor_articles.execute("SELECT article FROM articles WHERE ident in ({})"
                        .format(",".join([str(val) for val in a_article_ids])))
articles = [val[0] for val in cursor_articles.fetchall()]

# Queries
queries = [
    ['arnold', (0, 10), 'schwarzenegger', (0, 10), 'is'],
    ['apache', (0, 100), 'software'],
    ['aarhus', (30, 150), 'denmark'],
    ['english', (0, 100), 'alphabet'],
    ['first', (0, 85), 'letter', (0, 100), 'alphabet', (0, 200), 'consonant']
]

# Make queries
for query in queries:
    query_start = time()
    print(f"\nStarting query for {query}")
    results = 0
    matches = 0
    for article in articles:
        result = nested_search(query, article)
        if result:
            results += 1
            matches += len(result)
    print("Got {} results and {} matches in {:.2f}s".format(results, matches, time() - query_start))

print(f"\nAll 'A'-articles and all patterns matched in {time() - start:.2f}s")

########################################################################################
###############################################################################################################
########################################################################################
#
# All articles
#
print("\n\n" + "-" * 80)
print("All articles Search")
print("-" * 80)
start = time()

# Queries
queries = [
    ['elephants', (0, 20), 'are', (0, 20), 'to'],
    # ['technical', (0, 20), 'university', (0, 20), 'denmark'],
    # ['testing', (0, 20), 'with', (0, 20), 'a', (0, 30), 'lot', (0, 4), 'of', (0, 5), 'words'],
    # ['stress', (0, 250), 'test'],
    # ['object', (10, 200), 'application', (0, 100), 'python', (10, 200), 'system', (0, 100), 'computer',
    #  (0, 10), 'science', (0, 150), 'linux', (0, 200), 'ruby']
]

for query in queries:

    ########################################################################################
    # Search specification

    print(f"\nStarting query for {query}")

    # Start main timer
    search_start = time()

    ########################################################################################
    # Word substring search -> word set

    # Specific words
    search_words = [word for word in query if isinstance(word, str)]

    # Search for words as substrings in word-database
    matching_words = []
    for word_nr, word in enumerate(search_words):
        # Test string and pattern
        pattern = re.compile(word)

        # Find positions
        match_indices = [match.start() for match in pattern.finditer(massive_keys_string)]

        # Find keys
        located_keys = [key_index_list[match] for match in match_indices]

        # Append
        matching_words.append(located_keys)

    ########################################################################################
    # Words -> articles

    # Go through word-matches and determine related articles
    article_list_list = []
    for word_matches in matching_words:
        # Map words to articles
        cursor_words.execute("SELECT article_list FROM words WHERE ident in ({})"
                             .format(",".join([str(val) for val in word_matches])))
        articles = [val
                    for val_list in cursor_words.fetchall()
                    for val in json.loads(val_list[0])]
        article_list_list.append(articles)

    # Collective article set
    intersecting_articles = set(article_list_list[0])
    for article_set in article_list_list[1:]:
        intersecting_articles = intersecting_articles.intersection(set(article_set))

    ########################################################################################
    # Initial patterns match in article set

    # Pattern
    search_pattern = re.compile(task_re_pattern(query))

    # Database query
    cursor_articles.execute("SELECT ident, article FROM articles WHERE ident in ({})"
                            .format(",".join([str(val) for val in list(intersecting_articles)])))

    # Fetch articles and filter
    filtered_articles = dict()
    filtered_articles_results = dict()
    for idx in range(len(intersecting_articles)):

        # Get article
        fetch = cursor_articles.fetchone()
        if fetch is None:
            break
        article_nr, article = fetch

        search = search_pattern.search(article)
        if search:
            filtered_articles[article_nr] = article
            filtered_articles_results[article_nr] = search

    ########################################################################################
    # Recursive matching of pattern

    # Search results
    results = 0
    matches = 0

    # Go through filtered articles
    len(filtered_articles)
    for key_nr, key in enumerate(list(filtered_articles.keys())):
        result = nested_search(task_inputs=query, string=filtered_articles[key])
        if result:
            results += 1
            matches += len(result)

    print("Got {} results and {} matches in {:.2f}s".format(results, matches, time() - query_start))

print(f"\nAll articles and all patterns matched in {time() - start:.2f}s")
