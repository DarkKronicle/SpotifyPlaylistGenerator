import aiohttp
import matplotlib
from io import BytesIO

import seaborn as sns
import tekore as tk
from matplotlib import pyplot as plt
import numpy as np
import base64
from PIL import Image

from matplotlib.font_manager import fontManager, FontProperties


inter = "resources/Inter-Regular.ttf"
emoji = "resources/NotoEmoji-Bold.ttf"
fontManager.addfont(inter)
fontManager.addfont(emoji)
inter_prop = FontProperties(fname=inter)
emoji_prop = FontProperties(fname=emoji)

# https://github.com/catppuccin/catppuccin my beloved
colors = ['#74c7ec', '#94e2d5', '#f38ba8']


async def get_playlist_image(songs: list[tk.model.FullTrack], analysis: list[tk.model.AudioFeatures]):
    sns.set_theme(style="ticks", context="paper")
    sns.set(font=inter_prop.get_name() + "," + emoji_prop.get_name())
    sns.set_palette(sns.color_palette(colors))
    plt.style.use("dark_background")
    plt.figure(figsize=(3, 1.5))
    features = []
    for a in analysis:
        features.append((a.energy, a.valence, 1 - a.instrumentalness))

    data = np.array(features)
    ax = sns.violinplot(
        data=data,
        inner=None,
        saturation=1,
        orient='horizontal'
    )
    # ax.set_title(name, fontdict={
    #     'fontsize': 30,
    #     # 'horizontalalignment': 'left',
    # })
    ax.collections[0].set_edgecolor('white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.set_yticklabels(
        ['⚡', '☺', '🎤'], fontdict={
            'fontsize': 16,
            'color': '#a6adc8'
        }
    )
    ax.set_xticks([])

    for collection in ax.collections:
        if isinstance(collection, matplotlib.collections.PolyCollection):
            collection.set_edgecolor('#313244')
    # ax.set_yticks([])
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png', transparent=True, bbox_inches='tight', dpi=100)
    plt.clf()
    plt.close()
    buffer.seek(0)

    image = Image.new('RGB', (300, 300), (17, 17, 27))
    graph = Image.open(buffer)
    image.paste(graph, (10, 160), graph)

    try:
        album_images = []
        i = 0
        while len(album_images) < 2 and i < len(songs):
            if len(songs[i].album.images) == 0:
                i += 1
                continue
            url = songs[i].album.images[0].url
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as r:
                    if r.status != 200:
                        i += 1
                        continue
                    img_raw = await r.read()

            album_images.append(Image.open(BytesIO(img_raw)))
            i += 1

        if len(album_images) == 2:
            album_image = album_images[0]
            album_image = album_image.resize((150, 150))
            image.paste(album_image, (0, 0))
            album_image = album_images[1]
            album_image = album_image.resize((150, 150))
            image.paste(album_image, (150, 0))
    except:
        print("Couldn't make cover image")

    final_buffer = BytesIO()
    image.save(final_buffer, 'png')
    final_buffer.seek(0)

    return base64.b64encode(final_buffer.read()).decode()
