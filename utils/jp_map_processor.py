import os
import geopandas as gpd
import pandas as pd


def load_jp_map(geo_fn=None):
    if geo_fn is None:
        geo_fn = os.path.join(
            os.path.dirname(proj_folder), "japan-map", "data", "jp_map_simple.geojson"
        )

    gdf = gpd.read_file(geo_fn)
    for pref4 in ["和歌山", "神奈川", "鹿児島"]:
        gdf["N03_001"] = gdf["N03_001"].replace(pref4, pref4 + "県")
    gdf.loc[
        gdf[["N03_001", "N03_004"]].apply(tuple, axis=1) == ("高知県", "櫮原町"),
        "N03_004",
    ] = "條原町"
    gdf = gdf.reset_index()

    return gdf


def preprocess_jp_map(gdf):
    """
    Preprocesses a GeoDataFrame of Japanese administrative boundaries by:
    - Dissolving major cities and Tokyo wards into single geometries.
    - Adjusting and sorting administrative codes.
    - Removing duplicates and resetting the index.

    Parameters:
        gdf (GeoDataFrame): Input GeoDataFrame containing Japanese boundary data.

    Returns:
        GeoDataFrame: Cleaned and preprocessed GeoDataFrame.
    """
    # Ensure input GeoDataFrame is not modified
    gdf = gdf.copy(deep=True)

    # Ensure 'N03_007' is integer type
    gdf["N03_007"] = gdf["N03_007"].astype(int)

    # Extract major cities
    gdf_cities = gdf[gdf["N03_003"].isin(cities)].copy()

    # Process Tokyo wards
    gdf_tokyo = gdf[gdf["N03_004"].isin(tokyo_wards)].copy()
    gdf_tokyo["N03_003"] = "特別区部"

    # Combine cities and Tokyo wards
    gdf_cities = pd.concat([gdf_cities, gdf_tokyo]).to_crs(epsg=3099)

    # Dissolve geometries by 'N03_003' (city names)
    gdf_cities = gdf_cities.dissolve(by="N03_003").reset_index()

    # Update administrative fields
    gdf_cities["N03_004"] = gdf_cities["N03_003"]
    gdf_cities["N03_007"] -= 1

    # Transform CRS back to EPSG 6668
    gdf_cities = gdf_cities.to_crs(epsg=6668).sort_values("N03_007")

    # Remove processed cities from the original GeoDataFrame and append updated cities
    gdf_remaining = gdf[~gdf["N03_007"].isin(gdf_cities["N03_007"])]
    gdf_final = pd.concat([gdf_remaining, gdf_cities]).sort_values("N03_007")

    # Remove duplicates, reset index, and clean up columns
    gdf_final = gdf_final.drop_duplicates(subset=["N03_001", "N03_004"])
    gdf_final = gdf_final.reset_index(drop=True)

    return gdf_final


jp_main_cities = [
    "静岡市",
    "浜松市",
    "名古屋市",
    "岡山市",
    "広島市",
    "札幌市",
    "京都市",
    "大阪市",
    "堺市",
    "神戸市",
    "北九州市",
    "福岡市",
    "熊本市",
    "仙台市",
    "新潟市",
    "さいたま市",
    "千葉市",
    "横浜市",
    "川崎市",
    "相模原市",
    "特別区部",
]

cities_list_en = [
    "Sapporo",
    "Sendai",
    "Saitama",
    "Chiba",
    "Yokohama",
    "Kawasaki",
    "Sagamihara",
    "Niigata",
    "Shizuoka",
    "Hamamatsu",
    "Nagoya",
    "Kyoto",
    "Osaka",
    "Sakai",
    "Kobe",
    "Okayama",
    "Hiroshima",
    "Kitakyushu",
    "Fukuoka",
    "Kumamoto",
    "Tokyo",
]

tokyo_wards = [
    "千代田区",
    "中央区",
    "港区",
    "新宿区",
    "文京区",
    "台東区",
    "墨田区",
    "江東区",
    "品川区",
    "目黒区",
    "大田区",
    "世田谷区",
    "渋谷区",
    "中野区",
    "杉並区",
    "豊島区",
    "北区",
    "荒川区",
    "板橋区",
    "練馬区",
    "足立区",
    "葛飾区",
    "江戸川区",
]

cities = [
    "札幌市",
    "仙台市",
    "さいたま市",
    "千葉市",
    "横浜市",
    "川崎市",
    "相模原市",
    "新潟市",
    "静岡市",
    "浜松市",
    "名古屋市",
    "京都市",
    "大阪市",
    "堺市",
    "神戸市",
    "岡山市",
    "広島市",
    "北九州市",
    "福岡市",
    "熊本市",
]
