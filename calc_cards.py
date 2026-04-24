import csv
from itertools import combinations, product

ABILITY_DB_FILE = "ability_db.csv"
SUPPORT_CARD_DB_FILE = "support_card_db.csv"
OWNED_CARDS_FILE = "owned_cards.csv"


# kind → contextキー
KIND_TO_CONTEXT_KEY = {
    # SP
    "on_sp_vo": "sp_vo_count",
    "on_sp_da": "sp_da_count",
    "on_sp_vi": "sp_vi_count",
    "on_sp_20": "sp_total_count",

    # lesson
    "on_lesson_vo": "lesson_count",
    "on_lesson_da": "lesson_count",
    "on_lesson_vi": "lesson_count",

    # flat
    "flat_vo": None,
    "flat_da": None,
    "flat_vi": None,
    "flat_ssr_vo": None,
    "flat_ssr_da": None,
    "flat_ssr_vi": None,

    # param bonus
    "param_bonus_vo": "param_vo_total",
    "param_bonus_da": "param_da_total",
    "param_bonus_vi": "param_vi_total",
    "param_bonus_ssr_vo": "param_vo_total",
    "param_bonus_ssr_da": "param_da_total",
    "param_bonus_ssr_vi": "param_vi_total",

    # その他（既存）
    "on_normal_lesson": "normal_lesson_count",
    "on_enhance": "enhance_count",
    "on_enhance_A": "enhance_a_count",
    "on_enhance_M": "enhance_m_count",
    "on_delete_A": "delete_a_count",
    "on_delete_M": "delete_m_count",
    "on_delete": "delete_count",
    "on_convert": "convert_count",
    "get_active": "get_active_count",
    "get_mental": "get_mental_count",
    "get_buff": "get_buff_count",
    "get_energy": "get_energy_count",
    "get_impression": "get_impression_count",
    "get_reserve": "get_reserve_count",
    "get_ssr": "get_ssr_count",
    "on_class": "class_count",
    "on_supply": "supply_count",
    "on_consult": "consult_count",
    "on_outing": "outing_count",
    "on_rest": "rest_count",
    "on_exam_end": "exam_end_count",
    "on_special_training": "special_training_count",
    "get_drink": "get_drink_count",
    "on_drink_exchange": "drink_exchange_count",
    "on_customize": "customize_count",
    "get_item": "get_item_count",
    "on_param_event": "param_event_count",
    "on_param_event_ssr": "param_event_ssr_count",
    "get_focus": "get_focus_count",
    "get_motivation": "get_motivation_count",
    "get_all_out": "get_all_out_count",
}


def parse_int(text, default=0):
    text = str(text).strip()
    return int(text) if text else default


def parse_float(text, default=0.0):
    text = str(text).strip()
    return float(text) if text else default


def load_ability_db(filepath):
    result = {}

    with open(filepath, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ability_id = row["id"].strip()
            tier = row["tier"].strip()

            limit_raw = str(row.get("limit_count", "")).strip()
            limit_count = float(limit_raw) if limit_raw else -1.0  # -1 = 無制限

            result[(ability_id, tier)] = {
                "kind": row["kind"].strip(),
                "values": [
                    parse_float(row["I"]),
                    parse_float(row["II"]),
                    parse_float(row["III"]),
                    parse_float(row["IV"]),
                    parse_float(row["V"]),
                ],
                "limit_count": limit_count,
            }

    return result


def load_support_cards(filepath):
    result = []

    with open(filepath, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
           # if parse_int(row.get("implemented", 0)) != 1:
           #    continue

            result.append({
                "card_id": row["card_id"].strip(),
                "name": row["name"].strip(),
                "rarity": row["rarity"].strip(),
                "ability_tier": row["ability_tier"].strip(),
                "sp_rate": parse_int(row.get("sp_rate", 0)),
                "param_type": row["param_type"].strip(),

                "sense": parse_int(row.get("sense", 0)),
                "logic": parse_int(row.get("logic", 0)),
                "anomaly": parse_int(row.get("anomaly", 0)),
                "rental_candidate": parse_int(row.get("rental_candidate", 0)),

                "abilities": [
                    row.get("ab1", "none_id").strip() or "none_id",
                    row.get("ab2", "none_id").strip() or "none_id",
                    row.get("ab3", "none_id").strip() or "none_id",
                    row.get("ab4", "none_id").strip() or "none_id",
                    row.get("ab5", "none_id").strip() or "none_id",
                    row.get("ab6", "none_id").strip() or "none_id",
                    row.get("item", "none_id").strip() or "none_id",
                    
                ],
            })

    return result

def load_owned_cards(filepath):
    result = {}

    if hasattr(filepath, "getvalue"):
        text = filepath.getvalue().decode("utf-8-sig").splitlines()
        reader = csv.DictReader(text)
    else:
        f = open(filepath, "r", encoding="utf-8-sig", newline="")
        reader = csv.DictReader(f)

    for row in reader:
        if parse_int(row.get("owned", 0)) != 1:
            continue

        card_id = row["card_id"].strip()
        result[card_id] = get_limit_break_index(
            parse_int(row.get("limit_break", 0))
        )

    if not hasattr(filepath, "getvalue"):
        f.close()

    return result

def make_owned_cards(cards, owned_db):
    return [
        {**card, "limit_break": owned_db[card["card_id"]], "is_rental": False}
        for card in cards
        if card["card_id"] in owned_db
    ]


def make_rental_cards(cards):
    return [
        {**card, "limit_break": 4, "is_rental": True}
        for card in cards
        if card["rental_candidate"] == 1
    ]

def get_limit_break_index(limit_break):
    return max(0, min(4, limit_break))


def calc_ability_score(kind, value, context, limit_count):
    kind = kind.strip()

    if kind == "sp_rate":
        return 0.0

    if kind == "none":
        return 0.0

    if kind.startswith("flat"):
        return value

    if kind.startswith("param_bonus"):
        context_key = KIND_TO_CONTEXT_KEY[kind]
        return context[context_key] * (value / 100.0)

    context_key = KIND_TO_CONTEXT_KEY[kind]
    count = context[context_key]

    if limit_count >= 0:
        count = min(count, limit_count)

    return value * count


def calc_card_score(card, ability_db, context, limit_break=0):
    tier = card["ability_tier"]
    idx = get_limit_break_index(limit_break)

    total = 0.0

    for ability_id in card["abilities"]:
        ability = ability_db[(ability_id, tier)]

        score = calc_ability_score(
            ability["kind"],
            ability["values"][idx],
            context,
            ability["limit_count"]
        )

        total += score

    return total

def print_detail(card, ability_db, context):
    tier = card["ability_tier"]
    idx = get_limit_break_index(card["limit_break"])

    print("  内訳:")

    for ability_id in card["abilities"]:
        ability = ability_db[(ability_id, tier)]
        score = calc_ability_score(
            ability["kind"],
            ability["values"][idx],
            context,
            ability["limit_count"]
        )

        if ability_id != "none_id":
            print(
                f"    {ability_id}: "
                f"{score:.1f}"
            )


TYPE_ORDER = ("Vo", "Da", "Vi")

TREND_TO_TYPES = {
    "voda": ("Vo", "Da", "Vi"),
    "vovi": ("Vo", "Vi", "Da"),
    "davi": ("Da", "Vi", "Vo"),
}

PATTERN_COUNTS = {
    "3/3/0": (3, 3, 0),
    "3/2/1": (3, 2, 1),
    "2/2/2": (2, 2, 2),
}


def make_score_map(cards, ability_db, context):
    return {
        card["card_id"]: calc_card_score(
            card,
            ability_db,
            context,
            card["limit_break"]
        )
        for card in cards
    }


def make_type_patterns(context_name):
    trend = context_name.split("_")[-1]
    types = TREND_TO_TYPES[trend]

    return {
        name: dict(zip(types, counts))
        for name, counts in PATTERN_COUNTS.items()
    }


def group_cards_by_type(cards):
    return {
        card_type: [card for card in cards if card["param_type"] == card_type]
        for card_type in TYPE_ORDER
    }

def count_sp_cards(team):
    return sum(
        1 for card in team
        if "sp_rate_id" in card["abilities"]
    )

def get_display_score(card, own_score_map, rental_score_map):
    return (
        rental_score_map[card["card_id"]]
        if card.get("is_rental")
        else own_score_map[card["card_id"]]
    )

def _find_best_5(cards, score_map, pattern, min_sp, max_sp):
    groups = group_cards_by_type(cards)

    choices = [
        combinations(groups[card_type], pattern.get(card_type, 0))
        for card_type in TYPE_ORDER
    ]

    best_team = None
    best_score = -1.0

    for parts in product(*choices):
        team = [card for group in parts for card in group]
        sp_count = count_sp_cards(team)

        if not (min_sp <= sp_count <= max_sp):
            continue

        score = sum(score_map[card["card_id"]] for card in team)

        if score > best_score:
            best_team = team
            best_score = score

    return best_team, best_score

def find_best_team_by_pattern(
    own_cards,
    rental_cards,
    own_score_map,
    rental_score_map,
    pattern,
    min_sp=0,
    max_sp=6
):
    best_team = None
    best_score = -1.0
    best_rental = None

    for rental_card in rental_cards:
        remaining_pattern = pattern.copy()
        rental_type = rental_card["param_type"]
        remaining_pattern[rental_type] = remaining_pattern.get(rental_type, 0) - 1

        if any(count < 0 for count in remaining_pattern.values()):
            continue

        rental_sp = 1 if rental_card["sp_rate"] > 0 else 0

        own_candidates = [
            card for card in own_cards
            if card["card_id"] != rental_card["card_id"]
        ]

        own_team, own_score = _find_best_5(
            own_candidates,
            own_score_map,
            remaining_pattern,
            max(0, min_sp - rental_sp),
            max_sp - rental_sp
        )

        if own_team is None:
            continue

        team = list(own_team) + [rental_card]
        total_score = own_score + rental_score_map[rental_card["card_id"]]

        if total_score > best_score:
            best_team = team
            best_score = total_score
            best_rental = rental_card

    return best_team, best_score, best_rental

# --- DEBUG ---
# if ability_id != "none_id":
#     print(card["name"], ability_id, kind, value, ability["limit_count"], score)
# ---------------




CONTEXTS = {
#センスVoDa
    "sense_voda": {
        "param_vo_total": 955.0,
        "param_da_total": 955.0,
        "param_vi_total": 390.0,

        "sp_vo_count": 2.5,
        "sp_da_count": 2.5,
        "sp_vi_count": 0.0,

        "lesson_count": 2.5,
        "normal_lesson_count": 0.0,

        "enhance_count": 1.0,
        "enhance_a_count": 1.0,
        "enhance_m_count": 1.0,

        "delete_a_count": 1.0,
        "delete_m_count": 1.0,
        "delete_count": 1.0,
        "convert_count": 1.0,

        "get_active_count": 11.0,
        "get_mental_count": 11.0,
        "get_buff_count": 9.0,
        "get_focus_count": 9.0,
        "get_energy_count": 0.0,
        "get_motivation_count": 0.0,
        "get_impression_count": 0.0,
        "get_reserve_count": 10.0,
        "get_all_out_count": 1.0,
        "get_ssr_count": 8.0,

        "class_count": 4.0,
        "supply_count": 4.0,
        "consult_count": 2.0,
        "outing_count": 0.0,
        "rest_count": 0.0,
        "exam_end_count": 2.0,
        "special_training_count": 1.0,

        "get_drink_count": 23.0,
        "drink_exchange_count": 12.0,

        "customize_count": 5.0,
        "get_item_count": 5.0,
        "param_event_count": 1.0,
        "param_event_ssr_count": 1.0,
    },

#センスDaVi
    "sense_davi": {
        "param_vo_total": 390.0,
        "param_da_total": 955.0,
        "param_vi_total": 955.0,

        "sp_vo_count": 0.0,
        "sp_da_count": 2.5,
        "sp_vi_count": 2.5,

        "lesson_count": 2.5,
        "normal_lesson_count": 0.0,

        "enhance_count": 1.0,
        "enhance_a_count": 1.0,
        "enhance_m_count": 1.0,

        "delete_a_count": 1.0,
        "delete_m_count": 1.0,
        "delete_count": 1.0,
        "convert_count": 1.0,

        "get_active_count": 11.0,
        "get_mental_count": 11.0,
        "get_buff_count": 9.0,
        "get_focus_count": 9.0,
        "get_energy_count": 0.0,
        "get_motivation_count": 0.0,
        "get_impression_count": 0.0,
        "get_reserve_count": 10.0,
        "get_all_out_count": 1.0,
        "get_ssr_count": 8.0,

        "class_count": 4.0,
        "supply_count": 4.0,
        "consult_count": 2.0,
        "outing_count": 0.0,
        "rest_count": 0.0,
        "exam_end_count": 2.0,
        "special_training_count": 1.0,

        "get_drink_count": 23.0,
        "drink_exchange_count": 12.0,

        "customize_count": 5.0,
        "get_item_count": 5.0,
        "param_event_count": 1.0,
        "param_event_ssr_count": 1.0,
    },

#センスVoVi
    "sense_vovi": {
        "param_vo_total": 955.0,
        "param_da_total": 390.0,
        "param_vi_total": 955.0,

        "sp_vo_count": 2.5,
        "sp_da_count": 0.0,
        "sp_vi_count": 2.5,

        "lesson_count": 2.5,
        "normal_lesson_count": 0.0,

        "enhance_count": 1.0,
        "enhance_a_count": 1.0,
        "enhance_m_count": 1.0,

        "delete_a_count": 1.0,
        "delete_m_count": 1.0,
        "delete_count": 1.0,
        "convert_count": 1.0,

        "get_active_count": 11.0,
        "get_mental_count": 11.0,
        "get_buff_count": 9.0,
        "get_focus_count": 9.0,
        "get_energy_count": 0.0,
        "get_motivation_count": 0.0,
        "get_impression_count": 0.0,
        "get_reserve_count": 10.0,
        "get_all_out_count": 1.0,
        "get_ssr_count": 8.0,

        "class_count": 4.0,
        "supply_count": 4.0,
        "consult_count": 2.0,
        "outing_count": 0.0,
        "rest_count": 0.0,
        "exam_end_count": 2.0,
        "special_training_count": 1.0,

        "get_drink_count": 21.0,
        "drink_exchange_count": 12.0,

        "customize_count": 5.0,
        "get_item_count": 5.0,
        "param_event_count": 1.0,
        "param_event_ssr_count": 1.0,
    },

#やる気VoDa
    "motivation_voda": {
        "param_vo_total": 955.0,
        "param_da_total": 390.0,
        "param_vi_total": 955.0,

        "sp_vo_count": 2.5,
        "sp_da_count": 0.0,
        "sp_vi_count": 2.5,

        "lesson_count": 2.5,
        "normal_lesson_count": 0.0,

        "enhance_count": 1.0,
        "enhance_a_count": 0.0,
        "enhance_m_count": 0.0,

        "delete_a_count": 2.0,
        "delete_m_count": 2.0,
        "delete_count": 2.0,
        "convert_count": 2.0,

        "get_active_count": 8.0,
        "get_mental_count": 13.0,
        "get_buff_count": 0.0,
        "get_focus_count": 0.0,
        "get_energy_count": 0.0,
        "get_motivation_count": 0.0,
        "get_impression_count": 0.0,
        "get_reserve_count": 10.0,
        "get_all_out_count": 1.0,
        "get_ssr_count": 8.0,

        "class_count": 4.0,
        "supply_count": 4.0,
        "consult_count": 2.0,
        "outing_count": 0.0,
        "rest_count": 0.0,
        "exam_end_count": 2.0,
        "special_training_count": 1.0,

        "get_drink_count": 21.0,
        "drink_exchange_count": 12.0,

        "customize_count": 5.0,
        "get_item_count": 5.0,
        "param_event_count": 1.0,
        "param_event_ssr_count": 1.0,
    },

#アノマリーVoDa
    "anomaly_voda": {
        "param_vo_total": 955.0,
        "param_da_total": 955.0,
        "param_vi_total": 390.0,

        "sp_vo_count": 2.5,
        "sp_da_count": 2.5,
        "sp_vi_count": 0.0,

        "lesson_count": 2.5,
        "normal_lesson_count": 0.0,

        "enhance_count": 1.0,
        "enhance_a_count": 0.0,
        "enhance_m_count": 0.0,

        "delete_a_count": 2.0,
        "delete_m_count": 2.0,
        "delete_count": 2.0,
        "convert_count": 2.0,

        "get_active_count": 8.0,
        "get_mental_count": 13.0,
        "get_buff_count": 0.0,
        "get_focus_count": 0.0,
        "get_energy_count": 0.0,
        "get_motivation_count": 0.0,
        "get_impression_count": 0.0,
        "get_reserve_count": 10.0,
        "get_all_out_count": 1.0,
        "get_ssr_count": 8.0,

        "class_count": 4.0,
        "supply_count": 4.0,
        "consult_count": 2.0,
        "outing_count": 0.0,
        "rest_count": 0.0,
        "exam_end_count": 2.0,
        "special_training_count": 1.0,

        "get_drink_count": 21.0,
        "drink_exchange_count": 12.0,

        "customize_count": 5.0,
        "get_item_count": 5.0,
        "param_event_count": 1.0,
        "param_event_ssr_count": 1.0,
    },

#アノマリーDaVi
    "anomaly_davi": {
        "param_vo_total": 390.0,
        "param_da_total": 955.0,
        "param_vi_total": 955.0,

        "sp_vo_count": 0.0,
        "sp_da_count": 2.5,
        "sp_vi_count": 2.5,

        "lesson_count": 2.5,
        "normal_lesson_count": 0.0,

        "enhance_count": 1.0,
        "enhance_a_count": 0.0,
        "enhance_m_count": 0.0,

        "delete_a_count": 2.0,
        "delete_m_count": 2.0,
        "delete_count": 2.0,
        "convert_count": 2.0,

        "get_active_count": 8.0,
        "get_mental_count": 13.0,
        "get_buff_count": 0.0,
        "get_focus_count": 0.0,
        "get_energy_count": 0.0,
        "get_motivation_count": 0.0,
        "get_impression_count": 0.0,
        "get_reserve_count": 10.0,
        "get_all_out_count": 1.0,
        "get_ssr_count": 8.0,

        "class_count": 4.0,
        "supply_count": 4.0,
        "consult_count": 2.0,
        "outing_count": 0.0,
        "rest_count": 0.0,
        "exam_end_count": 2.0,
        "special_training_count": 1.0,

        "get_drink_count": 21.0,
        "drink_exchange_count": 12.0,

        "customize_count": 5.0,
        "get_item_count": 5.0,
        "param_event_count": 1.0,
        "param_event_ssr_count": 1.0,
    },

#アノマリーVoVi
    "anomaly_vovi": {
        "param_vo_total": 955.0,
        "param_da_total": 390.0,
        "param_vi_total": 955.0,

        "sp_vo_count": 2.5,
        "sp_da_count": 0.0,
        "sp_vi_count": 2.5,

        "lesson_count": 2.5,
        "normal_lesson_count": 0.0,

        "enhance_count": 1.0,
        "enhance_a_count": 0.0,
        "enhance_m_count": 0.0,

        "delete_a_count": 2.0,
        "delete_m_count": 2.0,
        "delete_count": 2.0,
        "convert_count": 2.0,

        "get_active_count": 8.0,
        "get_mental_count": 13.0,
        "get_buff_count": 0.0,
        "get_focus_count": 0.0,
        "get_energy_count": 0.0,
        "get_motivation_count": 0.0,
        "get_impression_count": 0.0,
        "get_reserve_count": 10.0,
        "get_all_out_count": 1.0,
        "get_ssr_count": 8.0,

        "class_count": 4.0,
        "supply_count": 4.0,
        "consult_count": 2.0,
        "outing_count": 0.0,
        "rest_count": 0.0,
        "exam_end_count": 2.0,
        "special_training_count": 1.0,

        "get_drink_count": 21.0,
        "drink_exchange_count": 12.0,

        "customize_count": 5.0,
        "get_item_count": 5.0,
        "param_event_count": 1.0,
        "param_event_ssr_count": 1.0,
    },
}

def calc_team_score(team, ability_db, context, limit_break):
    return sum(
        calc_card_score(card, ability_db, context, limit_break)
        for card in team
    )


def find_best_team(cards, ability_db, context, limit_break, team_size=6):
    scored_cards = [
        (card, calc_card_score(card, ability_db, context, limit_break))
        for card in cards
    ]

    best_team = None
    best_score = -1

    for team in combinations(scored_cards, team_size):
        total_score = sum(score for card, score in team)

        if total_score > best_score:
            best_score = total_score
            best_team = [card for card, score in team]

    return best_team, best_score

def make_card_detail(card, ability_db, context):
    tier = card["ability_tier"]
    idx = get_limit_break_index(card["limit_break"])

    details = []

    for ability_id in card["abilities"]:
        ability = ability_db[(ability_id, tier)]
        score = calc_ability_score(
            ability["kind"],
            ability["values"][idx],
            context,
            ability["limit_count"]
        )

        if ability_id != "none_id":
            details.append({
                "ability_id": ability_id,
                "kind": ability["kind"],
                "score": score,
            })

    return details

def run_calculation(selected_plan, context_name, min_sp, max_sp, owned_file=None):
    context = CONTEXTS[context_name].copy()

    context["sp_total_count"] = (
        context["sp_vo_count"] +
        context["sp_da_count"] +
        context["sp_vi_count"]
    )

    ability_db = load_ability_db(ABILITY_DB_FILE)
    cards = load_support_cards(SUPPORT_CARD_DB_FILE)
    owned_db = load_owned_cards(owned_file if owned_file is not None else OWNED_CARDS_FILE)

    cards = [card for card in cards if card[selected_plan] == 1]

    own_cards = make_owned_cards(cards, owned_db)
    rental_cards = make_rental_cards(cards)

    own_score_map = make_score_map(own_cards, ability_db, context)
    rental_score_map = make_score_map(rental_cards, ability_db, context)

    patterns = make_type_patterns(context_name)

    results = []

    for pattern_name, pattern in patterns.items():
        best_team, best_score, rental_card = find_best_team_by_pattern(
            own_cards,
            rental_cards,
            own_score_map,
            rental_score_map,
            pattern,
            min_sp,
            max_sp
        )

        if best_team is None:
            continue

        team_data = []

        for card in best_team:
            score = (
                rental_score_map[card["card_id"]]
                if card.get("is_rental")
                else own_score_map[card["card_id"]]
            )

            team_data.append({
                "name": card["name"],
                "score": score,
                "type": card["param_type"],
                "tier": card["ability_tier"],
                "sp_rate": card["sp_rate"],
                "is_rental": card.get("is_rental", False),
                "details": make_card_detail(card, ability_db, context),
            })

        results.append({
            "pattern": pattern_name,
            "total_score": best_score,
            "team": sorted(team_data, key=lambda x: x["score"], reverse=True)
        })

    return results

def main():
    import sys

    selected_plan = sys.argv[1] if len(sys.argv) > 1 else "anomaly"
    context_name = sys.argv[2] if len(sys.argv) > 2 else "anomaly_davi"

    min_sp = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    max_sp = int(sys.argv[4]) if len(sys.argv) > 4 else 6

    show_detail = len(sys.argv) > 5 and sys.argv[5] == "detail"

    context = CONTEXTS[context_name].copy()

    context["sp_total_count"] = (
        context["sp_vo_count"] +
        context["sp_da_count"] +
        context["sp_vi_count"]
    )

    ability_db = load_ability_db(ABILITY_DB_FILE)
    cards = load_support_cards(SUPPORT_CARD_DB_FILE)
    owned_db = load_owned_cards(OWNED_CARDS_FILE)

    cards = [card for card in cards if card[selected_plan] == 1]

    own_cards = make_owned_cards(cards, owned_db)
    rental_cards = make_rental_cards(cards)

    own_score_map = make_score_map(own_cards, ability_db, context)
    rental_score_map = make_score_map(rental_cards, ability_db, context)

    limit_break = 4

    own_score_map = make_score_map(own_cards, ability_db, context)
    rental_score_map = make_score_map(rental_cards, ability_db, context)
    patterns = make_type_patterns(context_name)

    print("=== 最適6枚編成 ===")
    print(f"plan: {selected_plan}")
    print(f"context: {context_name}")
    print(f"SP条件: {min_sp}〜{max_sp}枚")
    print()

    use_rental = True

    for pattern_name, pattern in patterns.items():
        best_team, best_score, rental_card = find_best_team_by_pattern(
            own_cards,
            rental_cards,
            own_score_map,
            rental_score_map,
            pattern,
            min_sp,
            max_sp
        )

        print(f"--- {pattern_name} ---")

        if best_team is None:
            print("条件を満たす編成が見つかりませんでした。")
            print()
            continue

        print(f"合計スコア: {best_score:.1f}")
        print(f"SP枚数: {count_sp_cards(best_team)}")

        for card in sorted(
            best_team,
            key=lambda c: get_display_score(c, own_score_map, rental_score_map),
            reverse=True
        ):
            score = get_display_score(card, own_score_map, rental_score_map)
            rental_mark = "【レンタル】" if card.get("is_rental") else ""

            print(
                f"{rental_mark}{card['name']:<20} "
                f"score={score:.1f}  "
                f"type={card['param_type']}  "
                f"tier={card['ability_tier']}  "
                f"sp_rate={card['sp_rate']}"
            )

            if show_detail:
                print_detail(card, ability_db, context)

        print()

if __name__ == "__main__":
    main()
