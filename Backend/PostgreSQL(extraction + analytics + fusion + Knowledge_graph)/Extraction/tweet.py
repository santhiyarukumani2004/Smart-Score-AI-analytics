import pandas as pd
import glob

# -----------------------------
# LOAD ALL CSV FILES
# -----------------------------
csv_path = r"F:\Project\Tweets\*.csv"
files = glob.glob(csv_path)

df_list = [pd.read_csv(file) for file in files]
tweets_df = pd.concat(df_list, ignore_index=True)

print("Total raw rows:", len(tweets_df))

# -----------------------------
# STANDARDIZE TEXT COLUMN
# -----------------------------
tweets_df['tweet_text'] = None

for col in ['text', 'Text', 'tweet', 'snippet', 'title']:
    if col in tweets_df.columns:
        tweets_df['tweet_text'] = tweets_df['tweet_text'].combine_first(tweets_df[col])

# Drop old text columns
tweets_df.drop(columns=['text', 'Text', 'tweet', 'snippet', 'title'], errors='ignore', inplace=True)

# Drop empty text
tweets_df.dropna(subset=['tweet_text'], inplace=True)

# Strip text
tweets_df['tweet_text'] = tweets_df['tweet_text'].astype(str).str.strip()

# -----------------------------
# FIX YEAR COLUMN (CRITICAL)
# -----------------------------
tweets_df['Year'] = pd.to_numeric(tweets_df.get('Year'), errors='coerce')

# Allow only realistic exam years
tweets_df.loc[
    (tweets_df['Year'] < 1990) | (tweets_df['Year'] > 2030),
    'Year'
] = None

tweets_df['Year'] = tweets_df['Year'].astype('Int64')

# -----------------------------
# MERGE PLATFORM / SUBJECT / TOPIC
# -----------------------------
tweets_df['platform'] = tweets_df.get('platform').fillna(tweets_df.get('Platform'))
tweets_df['subject']  = tweets_df.get('subject').fillna(tweets_df.get('Subject'))
tweets_df['topic']    = tweets_df.get('topic').fillna(tweets_df.get('Topic'))
tweets_df['link']     = tweets_df.get('link').fillna(tweets_df.get('Link'))

tweets_df.drop(columns=['Platform', 'Subject', 'Topic', 'Link'], errors='ignore', inplace=True)

# -----------------------------
# REMOVE DUPLICATES
# -----------------------------
tweets_df.drop_duplicates(subset=['tweet_text'], inplace=True)

# -----------------------------
# FINAL REPORT
# -----------------------------
print("\n✅ CLEANED DATASET")
print("Rows:", tweets_df.shape[0])
print("Columns:", tweets_df.shape[1])
print(tweets_df.isnull().sum())

# -----------------------------
# SAVE TO SINGLE CSV (BEST PRACTICE)
# -----------------------------
output_csv = r"F:\Project\Cleaned_Datasets\cleaned_tweets.csv"
tweets_df.to_csv(output_csv, index=False)

print(f"\n✅ Cleaned CSV saved at: {output_csv}")
