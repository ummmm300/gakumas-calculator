import streamlit as st

from calc_cards import run_calculation

st.title("サポカ計算機")

with open("owned_cards_template.csv", "r", encoding="utf-8-sig") as f:
    template_data = f.read()

st.download_button(
    "所持状況csvテンプレートをダウンロード",
    data=template_data,
    file_name="owned_cards_template.csv",
    mime="text/csv"
)
# ① プラン選択（先）
plan_labels = {
    "センス": "sense",
    "アノマリー": "anomaly",
}

selected_plan_label = st.selectbox(
    "プラン",
    list(plan_labels.keys())
)

plan = plan_labels[selected_plan_label]


# ② 傾向（あと）
context_labels = {
    "anomaly": {
        "VoDa": "anomaly_voda",
        "DaVi": "anomaly_davi",
        "VoVi": "anomaly_vovi",
    },
    "sense": {
        "VoDa": "sense_voda",
        "DaVi": "sense_davi",
        "VoVi": "sense_vovi",
    },
}

selected_label = st.selectbox(
    "傾向",
    list(context_labels[plan].keys())
)

context_name = context_labels[plan][selected_label]

min_sp = st.slider(
    "SP率サポカの最低枚数",
    min_value=0,
    max_value=6,
    value=2
)

max_sp = st.slider(
    "SP率サポカの最大枚数",
    min_value=min_sp,
    max_value=6,
    value=max(2, min_sp)
)

owned_file = st.file_uploader(
    "所持状況CSVをアップロード",
    type=["csv"]
)

if owned_file is None:
    st.warning("所持状況csvをアップロードしてください。")

if st.button("計算実行"):
    try:
        results = run_calculation(plan, context_name, min_sp, max_sp, owned_file)

        if not results:
            st.warning("条件を満たす編成が見つかりませんでした。所持カード、SP条件、プランを確認してください。")

        for result in results:
            st.subheader(f"{result['pattern']}（合計スコア {result['total_score']:.1f}）")

            for card in result["team"]:
                rental_mark = "【レンタル】" if card["is_rental"] else ""

                st.write(
                    f"{rental_mark}{card['name']} "
                    f"{card['score']:.1f} / "
                    f"{card['type']} / "
                    f"SP率 {card['sp_rate']}"
                )

    except ValueError as e:
        st.error(str(e))
    except Exception:
        st.error("予期しないエラーが発生しました。CSVの形式や入力内容を確認してください。")
    results = run_calculation(plan, context_name, min_sp, max_sp, owned_file)

    for result in results:
        st.subheader(f"{result['pattern']}（スコア {result['total_score']:.1f}）")
        st.write(f"合計スコア: {result['total_score']:.1f}")

        for card in result["team"]:
            rental_mark = "【レンタル】" if card["is_rental"] else ""
            st.write(
                f"{rental_mark}{card['name']} "
                f"{card['score']:.1f} / "
                f"{card['type']} / "
                f"SP率 {card['sp_rate']}"
            )

