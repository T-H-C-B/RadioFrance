import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

df = pd.read_csv('personnality_with_country.csv')

country_counts = df.groupby('country').size()
country_counts.name = 'count'

world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

world = world.merge(country_counts.reset_index(), left_on="name", right_on='country', how="left")
world = world.fillna(0)

fig, ax = plt.subplots(1, 1, figsize=(25, 20))
world.boundary.plot(ax=ax)


norm = LogNorm(vmin=world['count'].min() + 1, vmax=world['count'].max())

world.plot(column='count', ax=ax, legend=True,
           legend_kwds={'label': "Number of People by Country (Log Scale)"},
           norm=norm)

show = True

if show:
    for x, y, country, count in zip(world.geometry.representative_point().x,
                                    world.geometry.representative_point().y,
                                    world.name,
                                    world['count']):
        ax.text(x, y, f"{country}\n{int(count)}", fontsize=8, ha='center')



plt.show()
