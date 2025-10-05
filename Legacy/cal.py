# 하루 필요 열량 계산
# 레퍼런스: https://www.nasa.gov/wp-content/uploads/2023/03/nutritional-biochemistry-of-space-flight.pdf?emrc=68e06ad980adb p13 table 1 - ISS nutrients requirements
# 레퍼런스: https://www.fao.org/4/y5686e/y5686e07.htm#bm07.1 table 5.1, 5.2 - 하루 에너지 요구량
# 이 주석 이하 코드는 전부 AI의 도움을 받음.

# tee_calc.py
# 입력: weight(kg), age(years), sex('male'|'female'), activity (str or float)
# 반환: BMR(kcal/day), TEE(kcal/day)

from dataclasses import dataclass

@dataclass
class Person:
    weight: float
    age: int
    sex: str  # 'male' or 'female'
    activity: str | float  # 'sedentary','low','moderate','active','very_active' or numeric PAL

# Schofield coefficients by sex and age range (weight in kg)
# Format: (age_min_inclusive, age_max_inclusive, a_coeff, b_coeff) -> BMR = a*weight + b
SCHOFIELD = {
    'male': [
        (0, 3, 59.512, -30.4),
        (3, 10, 22.706, 504.3),
        (10, 18, 17.686, 658.2),
        (18, 30, 15.057, 692.2),
        (30, 60, 11.472, 873.1),
        (60, 120, 11.711, 587.7),  # older-adult coeff (Schofield includes >60 variant)
    ],
    'female': [
        (0, 3, 58.317, -31.1),
        (3, 10, 20.315, 485.9),
        (10, 18, 13.384, 692.6),
        (18, 30, 14.818, 486.6),
        (30, 60, 8.126, 845.6),
        (60, 120, 9.082, 658.5),
    ]
}

# Default PAL mappings (common categories). Users may supply numeric PAL directly.
PAL_MAP = {
    'sedentary': 1.40,
    'low': 1.55,
    'moderate': 1.75,
    'active': 1.90,
    'very_active': 2.20
}

def schofield_bmr(weight: float, age: int, sex: str) -> float:
    sex = sex.lower()
    if sex not in SCHOFIELD:
        raise ValueError("sex must be 'male' or 'female'")
    for (amin, amax, a, b) in SCHOFIELD[sex]:
        if amin <= age <= amax:
            return a * weight + b
    # fallback to closest age bracket
    brackets = SCHOFIELD[sex]
    if age < brackets[0][0]:
        a, b = brackets[0][2], brackets[0][3]
    else:
        a, b = brackets[-1][2], brackets[-1][3]
    return a * weight + b

def get_pal(activity: str | float) -> float:
    if isinstance(activity, (int, float)):
        pal = float(activity)
    else:
        key = str(activity).strip().lower()
        if key in PAL_MAP:
            pal = PAL_MAP[key]
        else:
            raise ValueError(f"Unknown activity '{activity}'. Use keys: {list(PAL_MAP.keys())} or numeric PAL.")
    if not (1.0 <= pal <= 3.0):
        raise ValueError("PAL value out of realistic range (1.0-3.0).")
    return pal

def calculate_tee(person: Person) -> dict:
    bmr = schofield_bmr(person.weight, person.age, person.sex)
    pal = get_pal(person.activity)
    tee = bmr * pal
    return {'BMR_kcal_per_day': round(bmr, 1), 'PAL': round(pal, 2), 'TEE_kcal_per_day': round(tee, 1)}

def need_nutrients(TEE_kcal_per_day): # 일일 에너지 필요를 탄단지 필요양으로 전환
    totalcarbohydrateg = 0.50 / 4 * TEE_kcal_per_day
    totalproteing = 0.15 / 4 * TEE_kcal_per_day
    totalfatg = 0.35 / 9 * TEE_kcal_per_day
    return totalcarbohydrateg, totalproteing, totalfatg

if __name__ == "__main__":
    # 예시 사용자 입력 — 변경 가능
    examples = [
        Person(weight=75, age=35, sex='male', activity='moderate'),
        Person(weight=60, age=28, sex='female', activity='low'),
        Person(weight=80, age=70, sex='male', activity=1.55),  # 직접 PAL 입력
    ]
    for p in examples:
        res = calculate_tee(p)
        print(f"{p.sex.title()}, age {p.age}, weight {p.weight} kg, activity {p.activity} -> BMR {res['BMR_kcal_per_day']} kcal/day, PAL {res['PAL']}, TEE {res['TEE_kcal_per_day']} kcal/day")
