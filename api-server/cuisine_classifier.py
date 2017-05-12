"""
A simple cuisine classifier based on fooditems
"""

import yaml

def load_yaml(data_yaml_file):
    with open(data_yaml_file, 'r') as f:
        data = yaml.load(f)
        return data


def tokenize(sentence, separator=': '):
    """
    Simple tokenization split
    :param sentence: input string
    :return: token (i.e words)
    """
    # For some foodtrucks the fooditems are separated by : or ;
    sentence.replace(';', ':')
    if separator not in sentence:
        separator = ' '  # some food items are only separated by space
    return sentence.split(separator)


def normalize(word):
    """
    Word normalizer

    Using this simple normalizer allow to easily compare words
    :param word: input word
    :return: a word
    """
    word = word.lower()
    # removing plural, it facilitates the matching
    if len(word)>0 and word[-1] == 's':
        return word[0:-1]
    return word

def preprocess_str(sentence):
    return [normalize(word) for word in tokenize(sentence)]


class CuisineClassifier(object):
    def __init__(self, data_yaml_file=None):
        """

        :param data_yaml_file:
        """
        if data_yaml_file is None:
            raise ValueError("A configuration file containing matching words is required")
        cuisines = load_yaml(data_yaml_file)
        self.cuisines_set = {k:set([normalize(w) for w in cuisines[k]]) for k in cuisines}

    def compute_match_cuisines(self, input_str, min_match=1):
        """
        Return the matching cuisines of a string

        :param input_str: input string
        :param min_match: minimal number of word hit to consider a cuisine as a match
        :return: list of cuisines that match the input string
        """
        match_cuisines = []
        no_match_cuisines = ['other']
        if input_str == '':
            return match_cuisines
        try:
            words = preprocess_str(input_str)
            for cuisine in self.cuisines_set:
                word_to_match_with = self.cuisines_set[cuisine]
                words_match = word_to_match_with.intersection(set(words))
                if len(words_match) >= min_match:
                    match_cuisines.append(cuisine)
            if len(match_cuisines) == 0:
                return no_match_cuisines
            return match_cuisines
        except Exception as e:
            print("Ignoring error {}, input was {}".format(e, input_str))
            return no_match_cuisines












