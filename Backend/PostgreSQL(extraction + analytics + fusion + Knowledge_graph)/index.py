# import nltk
# nltk.download('punkt')
# nltk.download('stopwords')

#MERGE CSV TO GET TOTAL RECORDS
import pandas as pd
import glob

csv_path = r"F:\Project\Tweets\*.csv"
files = glob.glob(csv_path)

df_list = []
for file in files:
    df = pd.read_csv(file)
    df_list.append(df)

tweets_df = pd.concat(df_list, ignore_index=True)

print("Total tweets:", len(tweets_df))

#STEP 1: BASIC DATASET INSPECTION (BEFORE CLEANING) (dataset overview)
print("📊 DATASET OVERVIEW (BEFORE CLEANING)")
print("-" * 50)

print(f"Total Rows    : {tweets_df.shape[0]}")
print(f"Total Columns : {tweets_df.shape[1]}")

print("\nColumn Names:")
print(list(tweets_df.columns))

print("\nMissing Values (per column):")
print(tweets_df.isnull().sum())

print("\nTotal Missing Values:", tweets_df.isnull().sum().sum())

duplicate_count = tweets_df.duplicated().sum()
print("\nDuplicate Rows:", duplicate_count)

#STEP 2: STANDARDIZE TEXT COLUMN
tweets_df['tweet_text'] = None

for col in ['text', 'Text', 'tweet', 'snippet', 'title']:
    if col in tweets_df.columns:
        tweets_df['tweet_text'] = (
            tweets_df['tweet_text']
            .combine_first(tweets_df[col])
        )

if 'text' in tweets_df.columns and 'tweet_text' not in tweets_df.columns:
    tweets_df.rename(columns={'text': 'tweet_text'}, inplace=True)

# STEP 3: HANDLE MISSING VALUES (SAFE STRATEGY)
# ✔ Drop rows where tweet text is missing (mandatory field)
tweets_df = tweets_df.dropna(subset=['tweet_text'])
tweets_df.drop(columns=['Unnamed: 3'], inplace=True, errors='ignore')

#create a single tweet text column
tweets_df['tweet_text'] = (
    tweets_df['text']
    .fillna(tweets_df['Text'])
    .fillna(tweets_df['tweet'])
    .fillna(tweets_df['snippet'])
    .fillna(tweets_df['title'])
)
#STEP 4: MERGE PLATFORM / SUBJECT / TOPIC
tweets_df.drop(
    columns=['text', 'Text', 'tweet', 'snippet', 'title'],
    inplace=True,
    errors='ignore'
)
tweets_df['platform'] = tweets_df['platform'].fillna(tweets_df['Platform'])
tweets_df['subject']  = tweets_df['subject'].fillna(tweets_df['Subject'])
tweets_df['topic']    = tweets_df['topic'].fillna(tweets_df['Topic'])
tweets_df['link']     = tweets_df['link'].fillna(tweets_df['Link'])
tweets_df.drop(
    columns=['Platform', 'Subject', 'Topic', 'Link'],
    inplace=True,
    errors='ignore'
)
# STEP 5: DROP EMPTY TEXT ROWS
tweets_df = tweets_df.dropna(subset=['tweet_text'])

tweets_df = tweets_df.drop_duplicates(subset=['tweet_text'])

# STEP 4: FILL OPTION COLUMNS
fill_defaults = {
    'platform': 'Twitter',
    'language': 'en',
    'topic': 'Unknown'
}

for col, value in fill_defaults.items():
    if col in tweets_df.columns:
        tweets_df[col] = tweets_df[col].fillna(value)

# STEP 5: REMOVE DUPLICATES
tweets_df = tweets_df.drop_duplicates()

# STEP 6: STANDARDIZE TEXT (BASIC CLEANING)
tweets_df['tweet_text'] = tweets_df['tweet_text'].astype(str).str.strip()

# STEP 7: FINAL DATASET INSPECTION (AFTER CLEANING)
print("\n📊 DATASET OVERVIEW (AFTER CLEANING)")
print("-" * 50)

print(f"Total Rows    : {tweets_df.shape[0]}")
print(f"Total Columns : {tweets_df.shape[1]}")

print("\nMissing Values (per column):")
print(tweets_df.isnull().sum())

duplicate_count_after = tweets_df.duplicated().sum()
print("\nDuplicate Rows:", duplicate_count_after)

# SAVE PREPROCESSING REPORT (FOR PROJECT FILE)
report = {
    "rows": tweets_df.shape[0],
    "columns": tweets_df.shape[1],
    "missing_values": tweets_df.isnull().sum().to_dict(),
    "duplicate_rows": duplicate_count_after
}

print("\n📄 Preprocessing Report:")
for k, v in report.items():
    print(f"{k}: {v}")


