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


def pattern_to_filename(pattern):
    return "".join([str(val).replace(", ", "_").replace(",", "_") for val in pattern]) + ".txt"


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
    vocabulary_words = pickle.load(Path(word_search_path, "vocabulary_words.p").open("rb"))
    vocabulary = pickle.load(Path(word_search_path, "vocabulary.p").open("rb"))
    massive_keys_string = pickle.load(Path(word_search_path, "massive_keys_string.p").open("rb"))
    key_index_list = pickle.load(Path(word_search_path, "key_index_list.p").open("rb"))
else:

    # Get all words and IDs
    cursor_words.execute("SELECT Ident, Word FROM words ORDER BY Ident")

    print("Creating vocabulary.")
    vocabulary = dict()
    max_id = 0
    fetch = cursor_words.fetchone()
    while fetch is not None:
        idx, word = fetch
        max_id = max(max_id, idx)
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
    key_index_list = [val
                      for word in keys
                      for val in [vocabulary[word]] * (len(word) + 1)]

    print("Making vocabulary words")
    vocabulary_words = [None] * (max_id + 1)
    for key, val in vocabulary.items():
        vocabulary_words[val] = key

    # Storage
    print("Storing files for word-search")
    pickle.dump(vocabulary_words, Path(word_search_path, "vocabulary_words.p").open("wb"))
    pickle.dump(vocabulary, Path(word_search_path, "vocabulary.p").open("wb"))
    pickle.dump(massive_keys_string, Path(word_search_path, "massive_keys_string.p").open("wb"))
    pickle.dump(key_index_list, Path(word_search_path, "key_index_list.p").open("wb"))

end = time()
print(f"Created / Loaded files in {end - start:.2f}s")

# Test
pattern = re.compile('elephants')
match_indices = [match.start() for match in pattern.finditer(massive_keys_string)]
located_keys = [key_index_list[match] for match in match_indices]
print('elephants', "is in", vocabulary_words[located_keys[0]])

output_path = Path(input_dir, "outputs")

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
    result = nested_search(query, article, identifier=cat_article_id)
    print("Got 1 results and {} matches in {:.2f}s".format(len(result), time() - query_start))

    with Path(output_path, "Cat_" + pattern_to_filename(query)).open("w") as file:
        for val in sorted(result):
            file.write("{:10d} : {:8d}-{:<8d}: {}\n".format(*val))

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
max_words_limit = 5000000
min_letters = 3

# Get 'a'-articles
a_article_ids = pickle.load(Path(input_dir, "a_articles.p").open("rb"))
print("Executing SQL fetch command")
cursor_articles.execute("SELECT article FROM articles WHERE ident in ({})"
                        .format(",".join([str(val) for val in a_article_ids])))
print("Fetching articles")
articles = [val[0] for val in cursor_articles.fetchall()]

# Queries
queries = [
    ['arnold', (0, 10), 'schwarzenegger', (0, 10), 'is'],
    ['apache', (0, 100), 'software'],
    ['aarhus', (30, 150), 'denmark'],
    ['english', (0, 100), 'alphabet'],
    ['first', (0, 85), 'letter', (0, 100), 'alphabet', (0, 200), 'consonant']
]


for query in queries:

    ########################################################################################
    # Search specification

    print(f"\nStarting query for {query}")

    # Start main timer
    query_start = time()

    ########################################################################################
    # Word substring search -> word set

    # Specific words
    search_words = []
    while not search_words:
        search_words = [word for word in query if isinstance(word, str) if len(word) >= min_letters]
        min_letters -= 1

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
        if len(located_keys) <= max_words_limit:
            matching_words.append(located_keys)

    # print("matching_words:", len(matching_words), sum([len(val) for val in matching_words]))

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
    intersecting_articles = set(a_article_ids)
    for article_set in article_list_list:
        intersecting_articles = intersecting_articles.intersection(set(article_set))

    # print("intersecting_articles:", len(intersecting_articles))

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
        if fetch is not None:
            article_nr, article = fetch

            search = search_pattern.search(article)
            if search:
                filtered_articles[article_nr] = article
                filtered_articles_results[article_nr] = search

    # print("filtered_articles_results:", len(filtered_articles_results))

    ########################################################################################
    # Recursive matching of pattern

    # Search results
    results = []
    matches = 0

    # Go through filtered articles
    len(filtered_articles)
    for key_nr, key in enumerate(list(filtered_articles.keys())):
        result = nested_search(task_inputs=query, string=filtered_articles[key], identifier=key_nr)
        if result:
            results.extend(result)
            matches += len(result)

    print("Got {} results and {} matches in {:.2f}s".format(len(results), matches, time() - query_start))

    with Path(output_path, "A_" + pattern_to_filename(query)).open("w") as file:
        for val in sorted(results):
            file.write("{:10d} : {:8d}-{:<8d}: {}\n".format(*val))

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
max_words_limit = 5000000
min_letters = 4

# Queries
queries = [
    ['elephants', (0, 20), 'are', (0, 20), 'to'],
    ['technical', (0, 20), 'university', (0, 20), 'denmark'],
    ['testing', (0, 20), 'with', (0, 20), 'a', (0, 30), 'lot', (0, 4), 'of', (0, 5), 'words'],
    ['stress', (0, 250), 'test'],
    ['object', (10, 200), 'application', (0, 100), 'python', (10, 200), 'system', (0, 100), 'computer',
     (0, 10), 'science', (0, 150), 'linux', (0, 200), 'ruby']
]

for query in queries:

    ########################################################################################
    # Search specification

    print(f"\nStarting query for {query}")

    # Start main timer
    query_start = time()

    ########################################################################################
    # Word substring search -> word set

    # Specific words
    search_words = []
    while not search_words:
        search_words = [word for word in query if isinstance(word, str) if len(word) >= min_letters]
        min_letters -= 1

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
        if len(located_keys) <= max_words_limit:
            matching_words.append(located_keys)

    # print("matching_words:", len(matching_words), sum([len(val) for val in matching_words]))

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

    # print("intersecting_articles:", len(intersecting_articles))

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
        if fetch is not None:
            article_nr, article = fetch

            search = search_pattern.search(article)
            if search:
                filtered_articles[article_nr] = article
                filtered_articles_results[article_nr] = search

    # print("filtered_articles_results:", len(filtered_articles_results))

    ########################################################################################
    # Recursive matching of pattern

    # Search results
    results = []
    matches = 0

    # Go through filtered articles
    len(filtered_articles)
    for key_nr, key in enumerate(list(filtered_articles.keys())):
        result = nested_search(task_inputs=query, string=filtered_articles[key], identifier=key_nr)
        if result:
            results.extend(result)
            matches += len(result)

    print("Got {} results and {} matches in {:.2f}s".format(len(results), matches, time() - query_start))

    with Path(output_path, "All_" + pattern_to_filename(query)).open("w") as file:
        for val in sorted(results):
            file.write("{:10d} : {:8d}-{:<8d}: {}\n".format(*val))

print(f"\nAll articles and all patterns matched in {time() - start:.2f}s")
