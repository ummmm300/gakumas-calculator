import streamlit as st

import csv
import io

from calc_cards import run_calculation, CONTEXTS

CONTEXT_LABELS_JP = {
    "param_vo_total": "レッスンで獲得したVoパラメータ",
    "param_da_total": "レッスンで獲得したDaパラメータ",
    "param_vi_total": "レッスンで獲得したViパラメータ",

    "sp_vo_count": "VoSPレッスン回数",
    "sp_da_count": "DaSPレッスン回数",
    "sp_vi_count": "ViSPレッスン回数",

    "lesson_count": "レッスン回数",
    "normal_lesson_count": "通常レッスン回数",

    "enhance_count": "強化回数",
    "enhance_a_count": "A札の強化回数",
    "enhance_m_count": "M札の強化回数",

    "delete_count": "削除回数",
    "delete_a_count": "A札の削除回数",
    "delete_m_count": "M札の削除回数",
    "convert_count": "チェンジ回数",

    "get_card_count": "カードの取得枚数",
    "get_active_count": "A札の取得枚数",
    "get_mental_count": "M札の取得枚数",
    "get_buff_count": "好調札の取得枚数",
    "get_focus_count": "集中札の取得枚数",
    "get_energy_count": "元気札の取得枚数",
    "get_motivation_count": "やる気札の取得枚数",
    "get_impression_count": "好印象札の取得枚数",
    "get_reserve_count": "温存札の取得枚数",
    "get_all_out_count": "全力札の取得枚数",
    "get_ssr_count": "SSR札の取得枚数", 

    "class_count": "授業回数",
    "supply_count": "差し入れ回数",
    "consult_count": "相談回数",
    "outing_count": "おでかけ回数",
    "rest_count": "休む回数",
    "exam_end_count": "試験終了回数",
    "special_training_count": "特別指導回数",

    "get_drink_count": "ドリンク獲得数",
    "drink_exchange_count": "相談ドリンク交換数",

    "customize_count": "カスタム回数",
    "get_item_count": "Pアイテム獲得数",
    "param_event_count": "パラメイベの回数",
    "param_event_ssr_count": "パラメイベの回数(配布SSR用)",

}

st.title("サポカ計算機")

st.warning("【重要】Web版を公開しました！今後はこちらの利用を推奨します👇")

st.markdown("👉 [サポカ計算機 Web版はこちら](https://support-card-web.vercel.app/)")

st.caption("v1.0.0｜サポカの画面入力・csv保存・ロジック対応・計算条件表示に対応")

st.markdown("[使い方はこちら](https://x.com/wandering_sen/status/2047936136153370971?s=20)")
st.markdown("[不具合報告・要望・意見などはこちらのDMまで](https://x.com/wandering_sen)")

with open("owned_cards_template.csv", "r", encoding="utf-8-sig") as f:
    template_data = f.read()


# ① プラン選択（先）
plan_labels = {
    "センス": "sense",
    "ロジック（やる気・元気）": "motivation",
    "ロジック（好印象）": "impression",
    "アノマリー": "anomaly",
}

selected_plan_label = st.selectbox(
    "プラン",
    list(plan_labels.keys())
)

plan = plan_labels[selected_plan_label]


# ② 傾向（あと）
context_labels = {
    "sense": {
        "VoDa": "sense_voda",
        "DaVi": "sense_davi",
        "VoVi": "sense_vovi",
    },
    "motivation": {
        "VoDa": "motivation_voda",
        "DaVi": "motivation_davi",
        "VoVi": "motivation_vovi",
    },
    "impression": {
        "VoDa": "impression_voda",
        "DaVi": "impression_davi",
        "VoVi": "impression_vovi",
    },
    "anomaly": {
        "VoDa": "anomaly_voda",
        "DaVi": "anomaly_davi",
        "VoVi": "anomaly_vovi",
    },
}

selected_label = st.selectbox(
    "傾向",
    list(context_labels[plan].keys())
)

context_name = context_labels[plan][selected_label]

with st.expander("計算条件を見る"):
    context = CONTEXTS[context_name]

    rows = []
    for key, value in context.items():
        label = CONTEXT_LABELS_JP.get(key, key)
        rows.append({"項目": label, "値": value})

    st.dataframe(rows, hide_index=True)

min_sp = st.slider(
    "SP率サポカの最低枚数",
    min_value=0,
    max_value=6,
    value=2
)

max_sp = 6

result_area = st.container()

run_button = st.button("計算実行")

from calc_cards import load_support_cards, SUPPORT_CARD_DB_FILE

cards = load_support_cards(SUPPORT_CARD_DB_FILE)

if "results" not in st.session_state:
    st.session_state.results = None

input_mode = st.radio(
    "所持状況の入力方法",
    ["画面で選択 (初回)", "csvアップロード(2回目以降)"]
)

save_area = st.container()

owned_file = None
if input_mode == "csvアップロード(2回目以降)":
    owned_file = st.file_uploader(
        "所持状況csvをアップロード",
        type=["csv"]
    )

else:
    st.info("所持カードを選択してください")

    search_text = st.text_input("カード名で検索")

    type_filter = st.selectbox(
        "タイプ絞り込み",
        ["全て", "Vo", "Da", "Vi"]
    )

    if "owned_ui" not in st.session_state:
        st.session_state.owned_ui = {}

    owned_ui = st.session_state.owned_ui

    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)

    writer.writerow(["card_id", "name", "owned", "limit_break"])

    for card in cards:
        card_id = card["card_id"]

        if card_id in owned_ui:
            writer.writerow([
                card_id,
                card["name"],
                1,
                owned_ui[card_id],
            ])
        else:
            writer.writerow([
                card_id,
                card["name"],
                0,
                0,
            ])

    if len(owned_ui) > 0:
        with save_area:
            st.download_button(
                "現在の所持状況をcsvで保存",
                data=csv_buffer.getvalue().encode("utf-8-sig"),
                file_name="owned_cards.csv",
                mime="text/csv"
            )
    from collections import Counter

    type_count = Counter(
        card["param_type"]
        for card in cards
        if card["card_id"] in owned_ui
    )

    st.write(
        f"選択中：{len(owned_ui)}枚 "
        f"(Vo{type_count['Vo']} / Da{type_count['Da']} / Vi{type_count['Vi']})"
    )

    cards_sorted = sorted(
        cards,
        key=lambda card: card["card_id"] in owned_ui
    )

    for card in cards_sorted:
        if search_text and search_text not in card["name"]:
            continue

        if type_filter != "全て" and card["param_type"] != type_filter:
            continue

        card_id = card["card_id"]

        checked = st.checkbox(
            card["name"],
            value=card_id in owned_ui,
            key=f"owned_{card_id}"
        )

        if checked:
            limit_break = st.selectbox(
                f"{card['name']} の凸数",
                [0, 1, 2, 3, 4],
                index=owned_ui.get(card_id, 4),
                key=f"lb_{card_id}"
            )

            owned_ui[card_id] = limit_break
        else:
            owned_ui.pop(card_id, None)

    with save_area:
        st.download_button(
            "csvテンプレートを保存",
            data=template_data,
            file_name="owned_cards_template.csv",
            mime="text/csv"
        )

    owned_file = owned_ui

if input_mode == "画面で選択" and len(owned_ui) == 0:
    st.warning("カードを1枚以上選択してください")

if run_button:
    if input_mode == "画面で選択 (初回)" and len(owned_ui) == 0:
        with result_area:
            st.info("所持カードが選択されていません。カードを選択してください。")
        st.stop()

    try:
        with st.spinner("計算中..."):
            results = run_calculation(plan, context_name, min_sp, max_sp, owned_file)

        with result_area:
            if not results:
                st.warning("条件を満たす編成が見つかりませんでした。所持カード、SP条件、プランを確認してください。")

            for result in results:
                st.markdown(f"### {result['pattern']}（合計スコア {result['total_score']:.1f}）")

                rows = []

                for card in result["team"]:
                    rows.append({
                        "レンタル": "〇" if card["is_rental"] else "",
                        "サポカ名": card["name"],
                        "点数": f"{card['score']:.1f}",
                        "タイプ": card["type"],
                        "SP率": card["sp_rate"],
                    })

                st.dataframe(rows, hide_index=True)

    except ValueError as e:
        with result_area:
            st.error(str(e))

    except Exception:
        with result_area:
            st.error("予期しないエラーが発生しました。CSVの形式や入力内容を確認してください。")
