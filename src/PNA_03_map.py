from pathlib import Path
import pandas as pd
# import matplotlib.pyplot as plt
import geopandas as gpd
import folium
import time

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

def main():
    # start time of function
    start_time = time.time()

    # project directory
    project_dir = str(Path(__file__).resolve().parents[1])

    # loading map data
    geo_path = r'\data\geo\administrative divide\Gminy.shp'
    map = gpd.read_file(project_dir + geo_path)
    # restricting dataframe
    map = map[['JPT_KOD_JE', 'geometry']]
    map['JPT_KOD_JE'] = map['JPT_KOD_JE'].apply(lambda x: str(x))

    # replacing wrong values in the dataframe
    teryt_dict = {'3001022': '3001023', '1420112': '1420113', '1438052': '1438053', '3007052': '3007053',
                  '0224032': '0224033', '2602092': '2602093', '1813022': '1813023', '0602062': '0602063',
                  '1409062': '1409063', '0608052': '0608053'}

    for wrong_teryt, corrrect_teryt in teryt_dict.items():
        map['JPT_KOD_JE'] = map['JPT_KOD_JE'].apply(lambda x: corrrect_teryt if x == wrong_teryt else x)

    map['JPT_KOD_JE'] = map['JPT_KOD_JE'].apply(lambda x: x[:6])
    teryt = map['JPT_KOD_JE']
    teryt.to_csv(project_dir + r'\data\interim\teryt.csv', index=False, encoding='UTF-8')

    # simplifying geometry
    map.geometry = map.geometry.simplify(0.005)

    # loading density data
    dens_path = r'\data\interim\240_groupby_dens.csv'
    density = pd.read_csv(project_dir + dens_path, sep=',')

    density.columns = ['teryt', 'density']

    # restricting dataframe
    density = density[['teryt', 'density']]

    # transforming teryt column
    density['teryt'] = density['teryt'].apply(lambda x: '0' + str(x) if len(str(x)) < 6 else str(x))
    # density['teryt'] = density['teryt'].apply(lambda x: '0' + str(x) if len(str(x)) < 7 else str(x))
    # density['teryt'] = density['teryt'].apply(lambda x: x[:6])

    print(density.head())
    print(density.dtypes)

    # changing data to GeoJSON
    map_geo = map.to_json()

    # creating folium map
    map_graph = folium.Map([52, 19], zoom_start=7)

    folium.Choropleth(geo_data=map_geo,
                      name='choropleth',
                      data=density,
                      columns=['teryt', 'density'],
                      key_on='feature.properties.JPT_KOD_JE',
                      fill_color='YlOrRd',
                      fill_opacity=0.7,
                      line_opacity=0.2,
                      legend_name="Population density in Poland").add_to(map_graph)

    # saving map
    print('saving map')
    map_graph.save(project_dir + r'\data\img\density.html')

    # end time of program + duration
    end_time = time.time()
    execution_time = int(end_time - start_time)
    print('\n', 'exectution time = ', execution_time, 'sec')

if __name__ == "__main__":
    main()
