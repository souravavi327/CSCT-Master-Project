from __future__ import annotations
import random
from datetime import datetime, timedelta
import pandas as pd


# ----------------------------
# 1) Configuration
# ----------------------------
SEED = 42
NUM_ROWS = 5000
START_DATE = datetime(2025, 6, 1)          # any start date is fine
DAYS_SPAN = 30                              # data spans 30 days
OUTPUT_PATH = "privacy_risk_monitoring_dataset.csv"

random.seed(SEED)

# Staff distribution (exact)
roles = (
    ["Doctor"] * 86 +
    ["Nurse"] * 166 +
    ["Admin"] * 15 +
    ["Receptionist"] * 21 +
    ["Pharmacist"] * 12
)

users = [f"U{str(i+1).zfill(3)}" for i in range(len(roles))]  # U001..U300
user_role_map = dict(zip(users, roles))

role_department = {
    "Doctor": "Clinical",
    "Nurse": "Clinical",
    "Pharmacist": "Pharmacy",
    "Admin": "Admin",
    "Receptionist": "Admin"
}

# Role-based risk weights (you can tune)
role_risk_weight = {
    "Doctor": 2,
    "Nurse": 3,
    "Pharmacist": 3,
    "Admin": 5,
    "Receptionist": 4
}

actions = ["View", "Edit", "Export"]
action_weights = [0.75, 0.20, 0.05]         # mostly View

sensitivities = ["Normal", "High"]
sensitivity_weights = [0.80, 0.20]          # mostly Normal

locations = ["Onsite", "Remote"]
location_weights = [0.75, 0.25]


# ----------------------------
# 2) Helper functions
# ----------------------------
def random_timestamp(start: datetime, days_span: int) -> datetime:
    minutes = random.randint(0, days_span * 24 * 60 - 1)
    return start + timedelta(minutes=minutes)

def is_weekend(day_name: str) -> int:
    return 1 if day_name in ["Saturday", "Sunday"] else 0

def is_off_hours(hour: int) -> int:
    # Clinic working hours assumed: 08:00–18:00 inclusive
    return 1 if (hour < 8 or hour > 18) else 0

def compute_risk_score(role: str, action: str, sensitivity: str, off_hours_flag: int) -> int:
    # Simple, interpretable scoring (you can tune):
    # base from role weight + penalty for high sensitivity + penalty for export + penalty for off-hours
    score = role_risk_weight[role] * 10
    if sensitivity == "High":
        score += 30
    if action == "Export":
        score += 20
    if off_hours_flag == 1:
        score += 20
    return score


# ----------------------------
# 3) Generate dataset
# ----------------------------
rows = []
for i in range(NUM_ROWS):
    user = random.choice(users)
    role = user_role_map[user]
    dept = role_department[role]

    ts = random_timestamp(START_DATE, DAYS_SPAN)
    hour = ts.hour
    day_name = ts.strftime("%A")

    weekend_flag = is_weekend(day_name)
    off_hours_flag = is_off_hours(hour)

    action = random.choices(actions, weights=action_weights, k=1)[0]
    sensitivity = random.choices(sensitivities, weights=sensitivity_weights, k=1)[0]
    location = random.choices(locations, weights=location_weights, k=1)[0]

    # AccessCountPerDay is a simulated daily volume indicator (not the count of rows).
    # Tune per role for realism.
    if role == "Doctor":
        access_count_per_day = random.randint(40, 90)
    elif role == "Nurse":
        access_count_per_day = random.randint(25, 60)
    elif role == "Pharmacist":
        access_count_per_day = random.randint(10, 30)
    elif role == "Admin":
        access_count_per_day = random.randint(5, 20)
    else:  # Receptionist
        access_count_per_day = random.randint(5, 15)

    risk_score = compute_risk_score(role, action, sensitivity, off_hours_flag)

    rows.append({
        "AccessID": f"A{str(i+1).zfill(5)}",
        "UserID": user,
        "UserRole": role,
        "Department": dept,
        "Timestamp": ts,
        "DayOfWeek": day_name,
        "HourOfDay": hour,
        "PatientID": f"P{random.randint(100, 999)}",
        "ActionType": action,
        "DataSensitivity": sensitivity,
        "AccessLocation": location,
        "AccessCountPerDay": access_count_per_day,
        "IsOffHours": off_hours_flag,
        "IsWeekend": weekend_flag,
        "RoleRiskWeight": role_risk_weight[role],
        "AccessRiskScore": risk_score
    })

df = pd.DataFrame(rows)


# ----------------------------
# 4) OPTIONAL: Inject evaluation scenarios (A–E)
#    Enable any of these blocks if you want guaranteed test cases.
# ----------------------------

# Scenario A: Admin at 03:00 Tuesday
def inject_scenario_a(df_: pd.DataFrame) -> None:
    admin_users = [u for u in users if user_role_map[u] == "Admin"]
    u = random.choice(admin_users)
    # Find a date that is a Tuesday within the span
    base = START_DATE
    while base.strftime("%A") != "Tuesday":
        base += timedelta(days=1)
    ts = base.replace(hour=3, minute=0, second=0, microsecond=0)
    row = {
        "AccessID": f"A{str(len(df_)+1).zfill(5)}",
        "UserID": u,
        "UserRole": "Admin",
        "Department": "Admin",
        "Timestamp": ts,
        "DayOfWeek": "Tuesday",
        "HourOfDay": 3,
        "PatientID": f"P{random.randint(100, 999)}",
        "ActionType": "View",
        "DataSensitivity": "Normal",
        "AccessLocation": "Remote",
        "AccessCountPerDay": 10,
        "IsOffHours": 1,
        "IsWeekend": 0,
        "RoleRiskWeight": role_risk_weight["Admin"],
        "AccessRiskScore": compute_risk_score("Admin", "View", "Normal", 1),
    }
    df_.loc[len(df_)] = row

# Scenario B: Receptionist extreme daily volume (set one row's AccessCountPerDay=500)
def inject_scenario_b(df_: pd.DataFrame) -> None:
    rec_users = [u for u in users if user_role_map[u] == "Receptionist"]
    u = random.choice(rec_users)
    idx = df_[df_["UserID"] == u].sample(1, random_state=SEED).index[0]
    df_.at[idx, "AccessCountPerDay"] = 500

# Scenario C: Non-clinical user with many High sensitivity accesses
def inject_scenario_c(df_: pd.DataFrame, n: int = 30) -> None:
    non_clin = [u for u in users if user_role_map[u] in ["Admin", "Receptionist"]]
    u = random.choice(non_clin)
    for _ in range(n):
        ts = random_timestamp(START_DATE, DAYS_SPAN)
        hour = ts.hour
        day_name = ts.strftime("%A")
        off_hours_flag = is_off_hours(hour)
        weekend_flag = is_weekend(day_name)
        action = random.choices(actions, weights=action_weights, k=1)[0]
        row = {
            "AccessID": f"A{str(len(df_)+1).zfill(5)}",
            "UserID": u,
            "UserRole": user_role_map[u],
            "Department": "Admin",
            "Timestamp": ts,
            "DayOfWeek": day_name,
            "HourOfDay": hour,
            "PatientID": f"P{random.randint(100, 999)}",
            "ActionType": action,
            "DataSensitivity": "High",
            "AccessLocation": "Remote",
            "AccessCountPerDay": random.randint(5, 20),
            "IsOffHours": off_hours_flag,
            "IsWeekend": weekend_flag,
            "RoleRiskWeight": role_risk_weight[user_role_map[u]],
            "AccessRiskScore": compute_risk_score(user_role_map[u], action, "High", off_hours_flag),
        }
        df_.loc[len(df_)] = row

# Scenario D: Sunday afternoon export
def inject_scenario_d(df_: pd.DataFrame) -> None:
    u = random.choice(users)
    # Find a Sunday within the span
    base = START_DATE
    while base.strftime("%A") != "Sunday":
        base += timedelta(days=1)
    ts = base.replace(hour=15, minute=0, second=0, microsecond=0)  # afternoon
    role = user_role_map[u]
    row = {
        "AccessID": f"A{str(len(df)+1).zfill(5)}",
        "UserID": u,
        "UserRole": role,
        "Department": role_department[role],
        "Timestamp": ts,
        "DayOfWeek": "Sunday",
        "HourOfDay": 15,
        "PatientID": f"P{random.randint(100, 999)}",
        "ActionType": "Export",
        "DataSensitivity": "High",
        "AccessLocation": "Remote",
        "AccessCountPerDay": 20,
        "IsOffHours": 0,
        "IsWeekend": 1,
        "RoleRiskWeight": role_risk_weight[role],
        "AccessRiskScore": compute_risk_score(role, "Export", "High", 0),
    }
    df_.loc[len(df_)] = row

# Scenario E: Normal doctor flow (50 during working hours)
def inject_scenario_e(df_: pd.DataFrame) -> None:
    doc_users = [u for u in users if user_role_map[u] == "Doctor"]
    u = random.choice(doc_users)
    base = START_DATE.replace(hour=10, minute=0, second=0, microsecond=0)  # standard hours
    ts = base
    row = {
        "AccessID": f"A{str(len(df)+1).zfill(5)}",
        "UserID": u,
        "UserRole": "Doctor",
        "Department": "Clinical",
        "Timestamp": ts,
        "DayOfWeek": ts.strftime("%A"),
        "HourOfDay": 10,
        "PatientID": f"P{random.randint(100, 999)}",
        "ActionType": "View",
        "DataSensitivity": "Normal",
        "AccessLocation": "Onsite",
        "AccessCountPerDay": 50,
        "IsOffHours": 0,
        "IsWeekend": is_weekend(ts.strftime("%A")),
        "RoleRiskWeight": role_risk_weight["Doctor"],
        "AccessRiskScore": compute_risk_score("Doctor", "View", "Normal", 0),
    }
    df_.loc[len(df_)] = row


df = df.head(NUM_ROWS)

# 5) Save

df.to_csv(OUTPUT_PATH, index=False)
print(f"Saved {len(df)} rows to {OUTPUT_PATH}")


