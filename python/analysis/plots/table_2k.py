import pandas as pd

def base_2k_to_latex(df):
    df['tp_yi'] =   df.apply(lambda row: f"({round(row['tp_y1'])}, {round(row['tp_y2'])}, {round(row['tp_y3'])})", axis=1)
    df['tp_y'] = df.apply(lambda row: round(row['tp_y_avg']), axis=1)
    df['rt_yi'] =   df.apply(lambda row: f"({round(row['rt_y1'],1)}, {round(row['rt_y2'],1)}, {round(row['rt_y3'],1)})", axis=1)
    df['rt_y'] = df.apply(lambda row: round(row['rt_y_avg'],1), axis=1)

    df['i'] = range(1, len(df['rt_y'])+1)

    df = df[['i', 'I', 'S', 'M', 'W', 'S-M', 'S-W', 'M-W', 'S-M-W', 'tp_yi', 'tp_y', 'rt_yi', 'rt_y']]

    rows = df.apply(lambda row: f"{row['i']} & {row['I']}\hphantom{{-}} & {row['S']}\hphantom{{-}} & {row['M']}\hphantom{{-}} & {row['W']}\hphantom{{--}} & {row['S-M']}\hphantom{{--}} & {row['S-W']}\hphantom{{--}} & {row['M-W']}\hphantom{{--}} & {row['S-M-W']}\hphantom{{---}} & {row['tp_yi']} & {row['tp_y']} & {row['rt_yi']} & {row['rt_y']} \\\\",axis=1)
    rows = rows.values

    before = """\\begin{tabular}{|c|rrrrrrrr|c|c|c|c|}
       \cline{10-13}
       \multicolumn{9}{c}{} & \multicolumn{2}{|c}{\\textbf{Throughput} (ops/sec)} & \multicolumn{2}{|c|}{\\textbf{Response Time} (ms)}\TBstrut\\\\
       \hline
       i & \hphantom{-}I\hphantom{-} & \hphantom{-}S\hphantom{-} & \hphantom{-}M\hphantom{-} &\hphantom{-}W\hphantom{-} & SM & SW & MW & SMW & ($y_{i1}, y_{i2}, y_{i3}$) & $\hat{y_i}$  & ($y_{i1}, y_{i2}, y_{i3}$) & $\hat{y_i}$\TBstrut\\\\
       \hline"""

    after = """   \hline
    \end{tabular}"""

    table = before

    for i, row in enumerate(rows):
        if i == 0:
            table+=f"\n   \Tstrut {row}"
        else:
            table+=f"\n   {row}"
    table += f"\n{after}"

    return table


def effect_2k_to_latex(df, tp_info, rt_info):
    tp_cols = [col for col in df.columns if '_tp' in col]
    df_tp = df[tp_cols].apply(lambda col: format_tpcol(col))
    df_tp  = df_tp .reset_index()
    df_tp['effect'] = df_tp.apply(lambda row: row['index'].split("_")[0], axis=1)
    df_tp = df_tp.drop('index', axis=1).rename(columns={0:"tp_str"})

    rt_cols = [col for col in df.columns if '_rt' in col]
    df_rt = df[rt_cols].apply(lambda col: format_rtcol(col))
    df_rt  = df_rt .reset_index()
    df_rt['effect'] = df_rt.apply(lambda row: row['index'].split("_")[0], axis=1)
    df_rt = df_rt.drop('index', axis=1).rename(columns={0:"rt_str"})

    df = df_tp.merge(df_rt)

    rows = df.apply(lambda row: f"{row['effect'].replace('-','')} & {row['tp_str']} & {row['rt_str']} \\\\",axis=1)
    rows = rows.values

    before = """\\begin{tabular}
       {|p{9mm}|% Factor
       p{8mm}% Tp Effect
       p{12mm}% Tp SS
       p{18.5mm}% Tp Variation
       p{22mm}|% Tp CI
       p{8mm}% Rt Effect
       p{12mm}% Rt SS
       p{18.5mm}% Rt Variation
       p{22mm}|} % Rt CI
       \cline{2-9}
       \multicolumn{1}{c}{} & \multicolumn{4}{|c}{\\textbf{Throughput} (ops/sec)} & \multicolumn{4}{|c|}{\\textbf{Response Time} (ms)}\TBstrut \\\\
       \hline
       \TBstrut Factor & Effect & Sum of\\newline Squares & Percentage\\newline of Variation & Confidence\\newline Interval 90\% & Effect & Sum of\\newline Squares & Percentage\\newline of Variation & Confidence\\newline Interval 90\%\\\\
       \hline"""

    after = """   \hline
    \end{tabular}"""

    table = before
    table += "\n\Tstrut"
    for i, row in enumerate(rows):
        table+= f"   {row}"
    table += f"Error & & ${int(round(tp_info['SSE']/1000))}k$\\rlft & ${round(tp_info['PERCENTAGE_OF_VARIATION_ERROR'],1)}$\\rlft & & & ${round(rt_info['SSE'],1)}$\\rlft & ${round(rt_info['PERCENTAGE_OF_VARIATION_ERROR'],1)}$\\rlft &\\\\"
    table += after
    return table

def format_tpcol(col):
    effect = int(round(col['effect']))
    ssj = int(round(col['SSj']/1000))
    variation = round(col['percentage_of_variation_effect'],1) if not pd.isna(col['percentage_of_variation_effect']) else " "
    ci_low = int(round(col['confidence_interval_low']))
    ci_high = int(round(col['confidence_interval_high']))
    significant = "^{\hphantom{a}}" if col['significant'] == 1.0 else "^{a}"

    return f"${effect}$\\rlft & ${ssj}$k\\rlft & ${variation}$\\rlft & $({ci_low},{ci_high}){significant}$\\rlft"

def format_rtcol(col):
    effect = round(col['effect'],1)
    ssj = int(round(col['SSj']))
    variation = round(col['percentage_of_variation_effect'],1) if not pd.isna(col['percentage_of_variation_effect']) else " "
    ci_low = round(col['confidence_interval_low'],1)
    ci_high = round(col['confidence_interval_high'],1)
    significant = "^{\hphantom{a}}" if col['significant'] == 1.0 else "^{a}"

    return f"${effect}$\\rlft & ${ssj}$\\rlft & ${variation}$\\rlft & $({ci_low},{ci_high}){significant}$\\rlft"
