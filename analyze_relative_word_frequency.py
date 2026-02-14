import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from wordfreq import top_n_list, word_frequency


def load_word_counts(json_path):
    """
    Load word counts from a JSON file.
    :param json_path: The path to the JSON file containing word counts.
    :type json_path: str

    :return: A dictionary of word counts if the file exists and is non-empty,
        otherwise None.
    :rtype: dict | None
    """
    if not os.path.exists(json_path):
        print(f"File {json_path} doesn't exist!")
        return None

    with open(json_path, 'r', encoding='utf-8') as f:
        word_counts_dict = json.load(f)
        if not word_counts_dict:
            print(f"File {json_path} is empty")
            return None
    return word_counts_dict


def get_frequency_df(word_counts_dict, mode, count, lang='en'):
    """
    The 'language' mode calculates frequencies for the top `count` words in the
    language, while the 'article' mode processes the most frequent words in the
    article. Frequencies are expressed in normalized values
    :param word_counts_dict: A dictionary where a word is a key and frequency
                             in the article is a value.
    :param mode: It can be 'language' to prioritize words from language or
             'article' to prioritize words from article.s
    :param count: The number of top words to include in the frequency data.
    :param lang: The language code of processed words.
    :return: A pandas DataFrame containing detailed frequency statistics. Each
        row represents a word and includes its normalized frequency in the
        article and its normalized frequency in the language
    """
    number_of_words = sum(word_counts_dict.values())
    word_counts_sorted = sorted(word_counts_dict.items(),
                                key=lambda x: x[1], reverse=True)

    # Maximum frequency of a word in the articles
    max_freq_article = word_counts_sorted[0][1] / number_of_words

    data = []
    if mode == 'language':
        # if count is too big, top_n_list automatically loads its maximum
        # number of records
        target_words = top_n_list(lang, count)
        max_freq_lang = word_frequency(target_words[0], lang)

        for word in target_words:
            article_freq = 0
            if number_of_words > 0:
                article_freq = (word_counts_dict.get(word, 0) /
                                number_of_words) / max_freq_article
            lang_freq = 0
            if max_freq_lang > 0:
                lang_freq = word_frequency(word, lang) / max_freq_lang

            data.append({
                "word": word,
                "frequency in the article": article_freq if article_freq > 0
                else None,  # None if word doesn't occur
                "frequency in the language": lang_freq
            })

    elif mode == 'article':
        # min(number of words, count) to deal with situations where `counts`
        # is larger than the number of words
        limit = min(len(word_counts_sorted), count)
        target_words = word_counts_sorted[:limit]

        # Get maximum frequency of a word in the language (for normalization)
        top_lang_word = top_n_list(lang, 1)[0]
        max_freq_lang = word_frequency(top_lang_word, lang)

        for word, count_val in target_words:
            article_freq = 0
            if number_of_words > 0:
                article_freq = (count_val /
                                number_of_words) / max_freq_article
            lang_freq = 0
            if max_freq_lang > 0:
                lang_freq = word_frequency(word, lang) / max_freq_lang

            data.append({
                "word": word,
                "frequency in the article": article_freq,
                "frequency in the language": lang_freq if lang_freq > 0
                else None
            })
    # If the user provided invalid mode, data is an empty dictionary.

    return pd.DataFrame(data)


def create_chart(df, chart_path):
    """
    Create a chart for the provided DataFrame and save it to a file with a
    given path.
    :param df: pandas DataFrame with values that will be displayed on a chart.
    :param chart_path: Path to a file where chart will be saved.
    """
    if not chart_path.endswith(".png"):
        print(f"Target file for chart should have .png extension. "
              f"Provided path: {chart_path}")
        return

    df_plot = df.set_index("word")
    df_plot = df_plot[['frequency in the article',
                       'frequency in the language']]
    df_plot.plot(
        kind='bar',
        figsize=(14, 7),
        color=['red', 'blue'],
    )

    plt.title("Frequency of some words on Wiki", fontsize=16)
    plt.xlabel("Word", fontsize=12)
    plt.ylabel("Normalized frequency [0..1]", fontsize=12)
    # Tilt the words by 45 degrees so they don't overlap
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    try:
        plt.savefig(chart_path)
    except Exception as e:
        print(f"Chart couldn't be saved in {chart_path}, error message: {e}")
    finally:
        plt.close()


def analyze_relative_word_frequency(mode, count, chart_path=None):
    """
    Analyzes the relative word frequency from a JSON file and prints
    frequency distribution. Optionally, generates and saves a chart
    representing the frequency distribution.

    :param mode: The mode of analysis to apply when processing the word
                 frequency data. Determines how the data is filtered or
                 grouped.
    :param count: The number of words to include in the analysis (if this
                  number is larger than the number of available words, then
                  the number of available words is included)
    :param chart_path: Optional path (with PNG extension) to save the
                       generated frequency chart as a file. If None, no
                       chart will be generated.
    :return: None
    """
    json_path = "./word-counts.json"
    lang = "en"

    word_counts_dict = load_word_counts(json_path)
    if word_counts_dict is None:
        return

    df = get_frequency_df(word_counts_dict, mode, count, lang)
    if df.empty:
        print("No data to display.")
        return

    print(df)

    if chart_path:
        create_chart(df, chart_path)
