import pandas as pd


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


def load_main_data():
    df_main = pd.read_csv("data/gen/jp_major_cities_rtpv_dataset.csv")

    # ======================================================================== #
    # Capacity Factor
    col_index = list(df_main.columns).index("pv_out") + 1
    df_main.insert(col_index, "cf", df_main["pv_out"].div(365 * 24))

    # ======================================================================== #
    # dmd_muni_res municipal residential demand
    col_index = list(df_main.columns).index("pref_res_ene_share") + 1
    df_main.insert(
        col_index, "dmd_muni_res", df_main["dmd_muni"] * df_main["pref_res_ene_share"]
    )
    df_main["dmd_muni_res"] = df_main["dmd_muni_res"].astype(int)

    # ======================================================================== #
    # dhouse_total
    col_index = list(df_main.columns).index("dhouse_new") + 1
    df_main.insert(
        col_index, "dhouse_total", df_main["dhouse_old"] + df_main["dhouse_new"]
    )
    df_main.insert(col_index + 1, "PV_max_new", df_main["dhouse_new"] * 4)
    df_main.insert(col_index + 2, "PV_max_all", df_main["dhouse_total"] * 4)
    # ======================================================================== #
    # Display

    return df_main


def build_data_columns(df):
    rpv_param_cols = df.filter(like="rpv_", axis=1).columns.to_list()
    muni_param_cols = [c for c in df.columns if c not in rpv_param_cols]

    rpv_cap_cols = df.filter(like="rpv_cap", axis=1).columns.to_list()
    rpv_no_cols = df.filter(like="rpv_no", axis=1).columns.to_list()

    return Dict(
        rpv_param=rpv_param_cols,
        muni_param=muni_param_cols,
        rpv_cap=rpv_cap_cols,
        rpv_no=rpv_no_cols,
    )


def set_muni_index(df):
    return df.reset_index().drop("pref", axis=1).set_index("muni")
