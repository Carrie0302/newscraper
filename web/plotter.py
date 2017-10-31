import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from helpers import timeit
import numpy as np
import seaborn as sns
import json


@timeit
def plot(url, name_clean):
    j_name = './static/{}.json'.format(name_clean)
    json_results = json.load(open(j_name))
    results_ = {k: v for k, v in json_results[0].items()}

    def get_spectrum(spec, name, colors):
        spec = dict(zip(spec, range(len(spec))))
        y, x = list(
            zip(*sorted(filter(lambda kv: kv[0] in spec, results_.items()), key=lambda kv: spec[kv[0]])))
        make_fig(x, y, name, colors)

    sns.set(style='whitegrid', font_scale=1.7)

    def label_cleaner(y):
        print(y)
        key = {
            'fakenews': 'fake news',
            'extremeright': 'extreme right',
            'extremeleft': 'extreme left',
            'veryhigh': 'very high veracity',
            'low': 'low veracity',
            'pro-science': 'pro science',
            'mixed': 'mixed veracity',
            'high': 'high veracity'
        }
        for label in y:
            for k, v in key.items():
                if label == k:
                    label = v.title()

            yield label.title()

    def make_fig(x, y, cat, colors='coolwarm_r'):

        y = list(label_cleaner(y))
        print(y)
        plt.figure(figsize=(8, 8))
        y_pos = np.arange(len(y))
        g = sns.barplot(y=y_pos, x=x, palette=colors, orient='h', saturation=.9)
        plt.yticks(y_pos, y)
        plt.title('{} - {}'.format(url, cat))
        plt.xlim(0, 0.4)

        plt.savefig(
            './static/{}.png'.format(name_clean + '_' + cat), format='png', bbox_inches='tight', dpi=200)
        plt.clf()

    get_spectrum(
        ['extremeright', 'right', 'right-center', 'center', 'left-center', 'left',
         'extremeleft'], 'Political', 'coolwarm_r')

    get_spectrum(['veryhigh', 'high', 'mixed', 'low', 'unreliable'], 'Accuracy', 'viridis')
    plt.close('all')

    get_spectrum(['conspiracy', 'fakenews', 'propaganda', 'pro-science', 'hate'], 'Character', 'husl')
