import pandas as pd
import numpy as np

house_old = ["01_1950年以前", "02_1951～1970年", "04_1971～1980年"]
house_new = [
    "05_1981～1990年",
    "06_1991～1995年",
    "07_1996～2000年",
    "08_2001～2005年",
    "09_2006～2010年",
    "10_2011～2013年",
    "11_2014年",
    "12_2015年",
    "13_2016年",
    "14_2017年",
    "15_2018年1月～9月",
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


class Dict(dict):
    """
    Dict is a subclass of dict, allowing you to access items
    in the dict using dot notation.
    """

    def __setattr__(self, name, value):
        self[name] = value

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(f"No attribute named '{item}'")

    def __delattr__(self, name):
        del self[name]

    def __dir__(self):
        return list(self.keys()) + super().__dir__()


def load_detached_house_data(file_loc):
    df_raw = pd.read_excel(file_loc, header=None)
    # 地域区分－全国・都道府県
    col_code_name = df_raw.columns[5]
    start_row = df_raw[col_code_name].to_list().index("地域区分－全国・都道府県")
    df_raw = df_raw.iloc[start_row + 1 :]

    data_col = [5, 7, 9, 11, 12]
    column_dict = {
        5: "admin",
        7: "cons_time",
        9: "cons_method",
        11: "floor_no",
        12: "total",
    }

    df = df_raw[data_col].rename(columns=column_dict)
    df.insert(0, "code", df["admin"].str.split("_").str[0])
    df.head()

    return df


def calc_japan_detached_house_statistics(df):
    # calculate the whole country statistics
    df_zenkoku = df[df["code"] == "00000"].copy()
    df_zenkoku_ikkodate = df_zenkoku[df_zenkoku["cons_method"] == "1_一戸建"].copy()
    is_old = df_zenkoku_ikkodate["cons_time"].isin(house_old)
    is_new = df_zenkoku_ikkodate["cons_time"].isin(house_new)
    is_total = df_zenkoku_ikkodate["floor_no"].isin(["00_総数"])
    zenkoku_ikkodate_old = df_zenkoku_ikkodate[is_total & is_old]["total"].sum()
    zenkoku_ikkodate_new = df_zenkoku_ikkodate[is_total & is_new]["total"].sum()
    zenkoku_old_ikkodate_share = (
        100 * zenkoku_ikkodate_old / (zenkoku_ikkodate_old + zenkoku_ikkodate_new)
    )
    zenkoku_ikkodate_total = zenkoku_ikkodate_old + zenkoku_ikkodate_new

    return Dict(
        total=zenkoku_ikkodate_total,
        old=zenkoku_ikkodate_old,
        new=zenkoku_ikkodate_new,
        old_share=zenkoku_old_ikkodate_share,
        new_share=100 - zenkoku_old_ikkodate_share,
    )


def extract_pref_city_code(df):
    # Process unique values from admin, splitting by underscore
    df_code_list = pd.Series(df["admin"].unique()).str.split("_", expand=True)
    df_code_list.columns = ["code", "admin"]
    df_code_list
    # Extract prefecture and municipality codes
    df_code_list["code_pref"] = df_code_list["code"].str[:2]
    df_code_list["code_muni"] = df_code_list["code"].str[2:]

    # filters
    is_zenkoku = df_code_list["code_pref"] == "00"
    is_pref = ~(df_code_list["code_pref"] == "00") & (
        df_code_list["code_muni"] == "000"
    )
    is_city = ~is_zenkoku & ~is_pref

    # translation
    code_to_admin_dict = df_code_list.set_index("code")["admin"].to_dict()

    # get codes
    pref_code = df_code_list[is_pref]["code"].to_list()
    city_code = df_code_list[is_city]["code"].to_list() + ["13100"]

    return pref_code, city_code, code_to_admin_dict


def extract_house_distribution(
    df,
    filter_condition,
    house_old,
    house_new,
    code_to_admin_dict,
    pref_code_dict,
    add_muni=True,
):

    # Filter, pivot, and calculate 'old' and 'new' values
    df_city_distri = df[filter_condition].pivot(
        index="code", columns="cons_time", values="total"
    )
    df_city_distri.columns.name = None
    df_city_distri.index.name = None

    df_city_distri = pd.concat(
        [
            df_city_distri[house_old].sum(axis=1).to_frame("old"),
            df_city_distri[house_new].sum(axis=1).to_frame("new"),
        ],
        axis=1,
    )

    # Calculate 'total' and 'old_share'
    df_city_distri["total"] = df_city_distri.sum(axis=1)
    df_city_distri["old_share"] = (
        (100 * df_city_distri["old"] / df_city_distri["total"]).astype("float").round(2)
    )

    # Add 'muni' and 'pref' columns
    if add_muni:
        df_city_distri.insert(0, "muni", df_city_distri.index.map(code_to_admin_dict))
    df_city_distri.insert(
        0, "pref", df_city_distri.index.str[:2].astype(int).map(pref_code_dict)
    )

    return df_city_distri


def calc_pref_city_distribution(df):
    # intermediate values that uses df as reference
    pref_code, city_code, code_to_admin_dict = extract_pref_city_code(df)
    pref_code_dict = {int(k[:2]): code_to_admin_dict[k] for k in pref_code}
    city_code_dict = {k: code_to_admin_dict[k] for k in city_code}

    # ============ Filters ============ #

    # cons_time filters
    is_old = df["cons_time"].isin(house_old)
    is_new = df["cons_time"].isin(house_new)
    is_old_n_new = df["cons_time"].isin(house_new + house_old)

    # cons_method filters
    is_ikkodate = df["cons_method"] == "1_一戸建"

    # floor_no filters
    all_floors = df["floor_no"] == "00_総数"

    # city filter
    is_tokyo = df["code"].str[:2] == "13"

    # ============ Prefecture Distribution ============ #
    filter_prefecture = (
        df["code"].isin(pref_code) & is_old_n_new & is_ikkodate & all_floors
    )
    df_pref_distribution = extract_house_distribution(
        df,
        filter_prefecture,
        house_old,
        house_new,
        code_to_admin_dict,
        pref_code_dict,
        add_muni=False,
    )

    df_pref_distribution = df_pref_distribution.sort_index()

    # ============ City Distribution ============ #

    # Create distribution for general cities
    filter_general = (
        df["code"].isin(city_code) & is_old_n_new & is_ikkodate & all_floors
    )
    df_city_distribution = extract_house_distribution(
        df, filter_general, house_old, house_new, code_to_admin_dict, pref_code_dict
    )
    df_city_distribution.sort_values("old_share", ascending=False, inplace=True)

    # Create distribution for Tokyo
    filter_tokyo = is_tokyo & is_old_n_new & is_ikkodate & all_floors
    df_city_distribution_tokyo = extract_house_distribution(
        df, filter_tokyo, house_old, house_new, code_to_admin_dict, pref_code_dict
    )

    # Update '13100' row in the general cities DataFrame
    df_city_distribution.loc["13100"] = df_city_distribution_tokyo.loc["13100"]

    df_city_distribution = df_city_distribution.sort_index()

    return df_pref_distribution, df_city_distribution
