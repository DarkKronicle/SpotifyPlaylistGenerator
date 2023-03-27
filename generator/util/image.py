import seaborn.categorical
seaborn.categorical._Old_Violin = seaborn.categorical._ViolinPlotter

# Monkey 🐒 patch for edge color https://stackoverflow.com/questions/49926147/how-to-modify-edge-color-of-violinplot-using-seaborn
# 🐒🐒🐒🐒🐒
class _My_ViolinPlotter(seaborn.categorical._Old_Violin):

    def __init__(self, *args, **kwargs):
        super(_My_ViolinPlotter, self).__init__(*args, **kwargs)
        self.gray = 'white'

seaborn.categorical._ViolinPlotter = _My_ViolinPlotter


from io import BytesIO

import seaborn as sns
import tekore as tk
from matplotlib import pyplot as plt
import numpy as np
import base64

from matplotlib.font_manager import fontManager, FontProperties

inter = "resources/Inter-Regular.ttf"
emoji = "resources/NotoEmoji-Bold.ttf"
fontManager.addfont(inter)
fontManager.addfont(emoji)
inter_prop = FontProperties(fname=inter)
emoji_prop = FontProperties(fname=emoji)


def get_playlist_image(name, analysis: list[tk.model.AudioFeatures]):
    sns.set_theme(style="ticks", context="paper")
    sns.set(font=inter_prop.get_name() + "," + emoji_prop.get_name())
    plt.style.use("dark_background")
    plt.figure(figsize=(3, 2.4))
    features = []
    for a in analysis:
        features.append((a.energy, a.valence, 1 - a.instrumentalness, max(0.0, min(1.0, ((a.tempo - 60) / 240)))))

    data = np.array(features)
    ax = sns.violinplot(
        data=data,
        inner=None,
        palette='Blues',
        saturation=1,
    )
    ax.set_title(name, fontdict={
        'fontsize': 30,
        # 'horizontalalignment': 'left',
    })
    ax.collections[0].set_edgecolor('white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.set_xticklabels(['⚡', '☺', '🎤', '🐇'], fontdict={
        'fontsize': 16,
    })
    ax.set_yticks([])
    plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95)
    # plt.show()

    buffer = BytesIO()
    plt.savefig(buffer, format='png', transparent=False, bbox_inches='tight', dpi=100)
    plt.clf()
    plt.close()
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode()
