
# DRUKSHIFT — Cryptocurrency Readiness in Bhutan
# Data Cleaning Script
# Author: Kinzang Choden
# Date: February 26, 202

import pandas as pd
import numpy as np

# STEP 1: Load the raw data 
df = pd.read_csv("Cryptocurrency Readiness in Bhutan.csv")
print(f"✅ Raw data loaded: {df.shape[0]} rows, {df.shape[1]} columns")

#  STEP 2: Rename columns to short, clean names 
df.columns = [
    "timestamp",
    "age_group",
    "occupation",
    "area",
    "internet_access",
    "device",
    "bank_access",
    "used_digital_payments",
    "payment_frequency",
    "payment_purpose",
    "q10_trust_digital",
    "q11_reliable_digital",
    "q12_security_concern",
    "q13_digital_familiarity",
    "q14_heard_crypto",
    "q15_crypto_understanding",
    "q16_barriers",
    "q17_what_helps",
    "q18_feel_ready",
    "q19_adopt_crypto",
    "q20_bhutan_readiness"
]
print("✅ Columns renamed")

#  STEP 3: Remove Under 18 respondents 
before = len(df)
df = df[df["age_group"] != "Under 18"]
print(f"✅ Removed Under 18: {before - len(df)} row(s) dropped")

#  STEP 4: Drop rows where age_group is missing 
df = df.dropna(subset=["age_group"])
print(f"✅ After removing missing age: {len(df)} rows remain")

#  STEP 5: Clean timestamp 
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
print("✅ Timestamp converted to datetime")

#  STEP 6: Standardize age_group 
df["age_group"] = df["age_group"].str.strip()
age_order = ["18-24", "25-34", "35-44", "45-54", "55+"]
df["age_group"] = pd.Categorical(df["age_group"], categories=age_order, ordered=True)

#  STEP 7: Standardize area 
# Fix any non-Bhutan areas (India, Singapore)  label as "Overseas"
df["area"] = df["area"].str.strip()
bhutan_areas = ["Urban", "Semi-Urban", "Rural"]
df["area"] = df["area"].apply(lambda x: x if x in bhutan_areas else "Overseas")
print("✅ Area standardized — non-Bhutan locations labeled as Overseas")

# ─ STEP 8: Standardize payment_frequency 
freq_map = {
    "Daily": "Daily",
    "most of the time ": "Daily",
    "Most of the time": "Daily",
    "Many times ": "Daily",
    "Often": "Often",
    "Weekly": "Weekly",
    "Occasionally": "Occasionally",
    "Sometimes ": "Occasionally",
    "Never": "Never",
    "I dont use": "Never",
}
df["payment_frequency"] = df["payment_frequency"].map(freq_map).fillna("Unknown")
print("✅ Payment frequency standardized")

#  STEP 9: Clean Likert scale columns (Q10, Q11, Q12, Q18) ─
#
# NUMBERING LOGIC:
# Q10 Trust        REVERSED: Strongly Agree = 5 (high trust is good, higher = better)
# Q11 Reliability  REVERSED: Strongly Agree = 5 (high reliability is good, higher = better)
# Q12 Security     NOT reversed: Strongly Agree = 1 (high concern = worried, lower = more worried)
# Q18 Feel Ready → REVERSED: Strongly Agree = 5 (high readiness is good, higher = better)

# Q12  extract number directly (1 = strongly agree = most worried, 5 = least worried)
df["q12_security_concern"] = df["q12_security_concern"].astype(str).str.extract(r"(\d)").astype(float)

# Q10 and Q11— extract number then reverse (so higher number = more positive)
reverse_map = {1.0: 5, 2.0: 4, 3.0: 3, 4.0: 2, 5.0: 1}
for col in ["q10_trust_digital", "q11_reliable_digital"]:
    extracted = df[col].astype(str).str.extract(r"(\d)")[0].astype(float)
    df[col] = extracted.map(reverse_map)

# Q18  map text to numbers (higher = more ready)
q18_map = {
    "Strongly agree": 5,
    "Agree": 4,
    "Neutral": 3,
    "Disagree": 2,
    "Strongly disagree": 1
}
df["q18_feel_ready"] = df["q18_feel_ready"].str.strip().map(q18_map)
print("✅ Likert scale columns cleaned and converted to numbers")

#  STEP 10: Clean Q13 digital familiarity
familiarity_map = {
    "Not familiar at all": 1,
    "Slightly familiar": 2,
    "Somewhat familiar": 3,
    "Very familiar": 4
}
df["q13_digital_familiarity_num"] = df["q13_digital_familiarity"].str.strip().map(familiarity_map)
print("✅ Q13 digital familiarity mapped to numbers")

#  STEP 11: Clean Q15 crypto understanding 
understanding_map = {
    "None": 1,
    "Very little": 2,
    "Basic": 3,
    "Good": 4
}
df["q15_crypto_understanding_num"] = df["q15_crypto_understanding"].str.strip().map(understanding_map)
# Fill missing with 1 (None) — people who skipped likely have no understanding
df["q15_crypto_understanding_num"] = df["q15_crypto_understanding_num"].fillna(1)
print("✅ Q15 crypto understanding mapped to numbers (missing filled with 1)")

# STEP 12: Clean Q19 adopt crypto 
adopt_map = {"No": 1, "Maybe": 2, "Yes": 3}
df["q19_adopt_crypto_num"] = df["q19_adopt_crypto"].str.strip().map(adopt_map)
print("✅ Q19 adopt crypto mapped to numbers")

# STEP 13: Clean Q20 Bhutan readiness 
# Standardize the varied text responses
def clean_q20(val):
    if pd.isna(val):
        return "Unknown"
    val = str(val).strip().lower()
    if "very ready" in val:
        return "Very ready"
    elif "somewhat ready" in val:
        return "Somewhat ready"
    elif "not very ready" in val or "not ready" in val:
        return "Not very ready"
    elif "not sure" in val or "no idea" in val or "i am not" in val:
        return "Unsure"
    else:
        return "Unsure"

df["q20_bhutan_readiness"] = df["q20_bhutan_readiness"].apply(clean_q20)
print("✅ Q20 Bhutan readiness standardized")

# STEP 14: Create Readiness Score
# Score = Q13 (1-4) + Q15 (1-4) + Q18 (1-5) + Q19 (1-3) = max 16
df["readiness_score"] = (
    df["q13_digital_familiarity_num"].fillna(2) +
    df["q15_crypto_understanding_num"].fillna(1) +
    df["q18_feel_ready"].fillna(3) +
    df["q19_adopt_crypto_num"].fillna(2)
)
print("✅ Readiness Score created (max = 16)")

# STEP 15: Create barrier flag columns 
df["barrier_poor_internet"]      = df["q16_barriers"].str.contains("Poor internet",    na=False).astype(int)
df["barrier_lack_of_knowledge"]  = df["q16_barriers"].str.contains("Lack of knowledge",na=False).astype(int)
df["barrier_security_concern"]   = df["q16_barriers"].str.contains("Security concern", na=False).astype(int)
df["barrier_complicated_tech"]   = df["q16_barriers"].str.contains("Complicated",      na=False).astype(int)
print("✅ Barrier flag columns created")

# STEP 16: Standardize Yes/No columns 
yes_no_cols = ["internet_access", "bank_access", "used_digital_payments", "q14_heard_crypto"]
for col in yes_no_cols:
    df[col] = df[col].str.strip().str.capitalize()
print("✅ Yes/No columns standardized")

# STEP 17: Clean occupation 
occ_map = {
    "Student": "Student",
    "Working professional": "Working Professional",
    "self-employed/enterpreneur": "Self-Employed",
    "Unemployed": "Unemployed",
    "Retired": "Retired",
    "Housewife": "Housewife",
    "Unemployed (housewife)": "Housewife",
    "Civil servant": "Civil Servant",
    "Fresh graduate": "Fresh Graduate",
    "Overseas employee": "Overseas Employee",
    "Unemployed. I am looked after by my children.": "Unemployed",
}
df["occupation"] = df["occupation"].str.strip().map(occ_map).fillna("Other")
print("✅ Occupation standardized")

# STEP 18: Final check 
print("\n" + "="*50)
print("FINAL CLEANED DATA SUMMARY")
print("="*50)
print(f"Total respondents: {len(df)}")
print(f"\nAge group distribution:\n{df['age_group'].value_counts().sort_index()}")
print(f"\nArea distribution:\n{df['area'].value_counts()}")
print(f"\nMissing values in key columns:")
key_cols = ["age_group", "occupation", "area", "q13_digital_familiarity_num",
            "q15_crypto_understanding_num", "q18_feel_ready", "q19_adopt_crypto_num", "readiness_score"]
print(df[key_cols].isnull().sum())
print(f"\nReadiness Score stats:\n{df['readiness_score'].describe().round(2)}")

#  STEP 19: Save cleaned data 
df.to_csv("Cryptocurrency-Readiness-Cleaned.csv", index=False)
print("\n✅ Cleaned data saved as: Cryptocurrency-Readiness-.csv")
print(" Data cleaning complete!")