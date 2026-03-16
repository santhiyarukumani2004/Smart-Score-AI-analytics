# # memes_processor.py
# import pandas as pd
# import glob
# import os
# import re
# from datetime import datetime
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# class MemesDatasetProcessor:
#     def __init__(self, csv_path):
#         self.csv_path = csv_path
#         self.df = None
        
#     def load_and_merge_files(self):
#         """Load and merge all CSV files"""
#         logger.info(f"Loading CSV files from: {self.csv_path}")
#         files = glob.glob(self.csv_path)
#         logger.info(f"Found {len(files)} CSV files")
        
#         df_list = []
#         for file in files:
#             try:
#                 df = pd.read_csv(file, encoding='utf-8', encoding_errors='ignore')
#                 df['source_file'] = os.path.basename(file)
#                 df_list.append(df)
#                 logger.info(f"Loaded {file}: {len(df)} rows")
#             except Exception as e:
#                 logger.error(f"Error loading {file}: {e}")
        
#         if df_list:
#             self.df = pd.concat(df_list, ignore_index=True)
#             logger.info(f"Total memes after merge: {len(self.df)}")
#             return True
#         return False
    
#     def dataset_overview(self, stage="BEFORE CLEANING"):
#         """Print dataset overview"""
#         print(f"\n📊 DATASET OVERVIEW ({stage})")
#         print("-" * 60)
        
#         if self.df is None:
#             print("No data loaded!")
#             return
        
#         print(f"Total Rows    : {self.df.shape[0]:,}")
#         print(f"Total Columns : {self.df.shape[1]}")
        
#         print("\nColumn Names:")
#         cols = list(self.df.columns)
#         for i in range(0, len(cols), 5):
#             print("  " + ", ".join(cols[i:i+5]))
        
#         print("\nMissing Values (top 15 columns):")
#         missing = self.df.isnull().sum().sort_values(ascending=False).head(15)
#         for col, count in missing.items():
#             pct = (count / len(self.df)) * 100
#             print(f"  {col}: {count:,} ({pct:.1f}%)")
        
#         print(f"\nTotal Missing Values: {self.df.isnull().sum().sum():,}")
#         print(f"Duplicate Rows: {self.df.duplicated().sum():,}")
#         print(f"Memory Usage: {self.df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
#     def clean_column_names(self):
#         """Standardize column names"""
#         self.df.columns = [str(col).lower().strip().replace(' ', '_') for col in self.df.columns]
#         logger.info("Column names standardized")
        
#     def safe_fill_columns(self):
#         """Safely fill missing values from backup columns"""
#         # Define column mappings (main_column: [backup_columns])
#         column_mappings = {
#             'platform': ['platform', 'source', 'app', 'site'],
#             'subject': ['subject', 'category', 'topic', 'theme'],
#             'topic': ['topic', 'subject', 'theme', 'category'],
#             'link': ['link', 'url', 'source_url', 'image_url'],
#             'image_path': ['image_path', 'image', 'img_path', 'thumbnail'],
#             'text': ['text', 'text_content', 'content', 'caption', 'ocr_text'],
#             'title': ['title', 'title_text', 'heading'],
#             'emoji': ['emoji', 'emojis', 'emojis_found'],
#             'year': ['year', 'date', 'collected_at']
#         }
        
#         for main_col, backup_cols in column_mappings.items():
#             if main_col not in self.df.columns:
#                 # Find first backup column that exists
#                 for backup in backup_cols:
#                     if backup in self.df.columns:
#                         self.df[main_col] = self.df[backup]
#                         logger.info(f"Created '{main_col}' from '{backup}'")
#                         break
#             else:
#                 # Fill missing values from backup columns
#                 for backup in backup_cols:
#                     if backup in self.df.columns and backup != main_col:
#                         self.df[main_col] = self.df[main_col].fillna(self.df[backup])
#                         logger.info(f"Filled '{main_col}' from '{backup}'")
    
#     def create_final_text(self):
#         """Create final text column from multiple sources"""
#         # Priority order for text sources
#         text_sources = [
#             'ocr_text',
#             'text_content', 
#             'text',
#             'title',
#             'title_text',
#             'snippet',
#             'caption'
#         ]
        
#         # Initialize final_text with empty string
#         self.df['final_text'] = ''
        
#         # Combine text from all available sources
#         for source in text_sources:
#             if source in self.df.columns:
#                 # Fill empty final_text with source
#                 mask = (self.df['final_text'].str.len() == 0) | (self.df['final_text'].isna())
#                 self.df.loc[mask, 'final_text'] = self.df.loc[mask, source].fillna('')
#                 logger.info(f"Added '{source}' to final_text")
        
#         # Remove rows with empty final_text
#         initial_count = len(self.df)
#         self.df = self.df[self.df['final_text'].str.len() > 0].copy()
#         removed = initial_count - len(self.df)
#         logger.info(f"Removed {removed} rows with empty text")
        
#         # Clean final_text
#         self.df['final_text'] = self.df['final_text'].astype(str).apply(self.clean_text)
    
#     def clean_text(self, text):
#         """Clean individual text"""
#         if pd.isna(text):
#             return ""
        
#         # Convert to string
#         text = str(text)
        
#         # Remove special characters but keep basic punctuation
#         text = re.sub(r'[^\w\s.,!?-]', ' ', text)
        
#         # Remove extra whitespace
#         text = ' '.join(text.split())
        
#         # Truncate if too long
#         if len(text) > 1000:
#             text = text[:1000]
            
#         return text.strip()
    
#     def extract_metadata(self):
#         """Extract additional metadata"""
#         # Extract year if present
#         if 'year' in self.df.columns:
#             self.df['year'] = pd.to_numeric(self.df['year'], errors='coerce')
#         else:
#             # Try to extract year from date columns
#             date_cols = ['date', 'collected_at', 'timestamp']
#             for col in date_cols:
#                 if col in self.df.columns:
#                     self.df['year'] = pd.to_datetime(self.df[col], errors='coerce').dt.year
#                     break
        
#         # Extract emojis
#         if 'emoji' in self.df.columns:
#             self.df['has_emoji'] = self.df['emoji'].notna()
#         else:
#             # Try to find emojis in text
#             import emoji
#             self.df['has_emoji'] = self.df['final_text'].apply(
#                 lambda x: any(c in emoji.EMOJI_DATA for c in str(x))
#             )
    
#     def remove_noise(self):
#         """Remove noisy data"""
#         initial_count = len(self.df)
        
#         # Remove duplicates based on final_text
#         self.df = self.df.drop_duplicates(subset=['final_text'], keep='first')
#         logger.info(f"Removed {initial_count - len(self.df)} duplicates")
        
#         # Remove very short texts (less than 3 characters)
#         initial_count = len(self.df)
#         self.df = self.df[self.df['final_text'].str.len() >= 3]
#         logger.info(f"Removed {initial_count - len(self.df)} very short texts")
        
#         # Remove rows with too many special characters
#         def is_noisy(text):
#             if len(text) == 0:
#                 return True
#             # Calculate ratio of alphanumeric characters
#             alnum = sum(c.isalnum() for c in text)
#             ratio = alnum / len(text)
#             return ratio < 0.5  # More than 50% special characters
        
#         initial_count = len(self.df)
#         self.df = self.df[~self.df['final_text'].apply(is_noisy)]
#         logger.info(f"Removed {initial_count - len(self.df)} noisy texts")
    
#     def drop_useless_columns(self):
#         """Drop columns that are mostly empty or useless"""
#         # Columns to always drop (index columns, etc.)
#         useless_patterns = ['unnamed', 'index', 'id_']
        
#         cols_to_drop = []
#         for col in self.df.columns:
#             # Check if column matches useless patterns
#             if any(pattern in col.lower() for pattern in useless_patterns):
#                 cols_to_drop.append(col)
#             # Check if column is mostly empty (>90% missing)
#             elif self.df[col].isnull().sum() / len(self.df) > 0.9:
#                 cols_to_drop.append(col)
        
#         if cols_to_drop:
#             self.df.drop(columns=cols_to_drop, inplace=True, errors='ignore')
#             logger.info(f"Dropped useless columns: {cols_to_drop}")
    
#     def add_analysis_columns(self):
#         """Add analysis columns for sentiment etc."""
#         # Add text statistics
#         self.df['text_length'] = self.df['final_text'].str.len()
#         self.df['word_count'] = self.df['final_text'].str.split().str.len()
        
#         # Add placeholder for future analysis
#         self.df['sentiment'] = 'neutral'
#         self.df['sentiment_score'] = 0.0
#         self.df['is_sarcastic'] = False
        
#         # Add timestamps
#         self.df['processed_at'] = datetime.now()
    
#     def save_processed_data(self, output_path):
#         """Save processed data to CSV"""
#         # Select important columns to save
#         important_cols = [
#             'final_text', 'platform', 'subject', 'topic', 'link',
#             'image_path', 'year', 'has_emoji', 'text_length', 'word_count',
#             'sentiment', 'is_sarcastic', 'source_file'
#         ]
        
#         # Keep only columns that exist
#         save_cols = [col for col in important_cols if col in self.df.columns]
        
#         # Add any other non-null columns
#         for col in self.df.columns:
#             if col not in save_cols and self.df[col].notna().sum() > len(self.df) * 0.1:
#                 if col not in ['final_text']:  # Avoid duplication
#                     save_cols.append(col)
        
#         output_df = self.df[save_cols].copy()
        
#         # Save to CSV
#         output_df.to_csv(output_path, index=False, encoding='utf-8')
#         logger.info(f"Saved processed data to {output_path}")
#         logger.info(f"Final dataset: {len(output_df)} rows, {len(output_df.columns)} columns")
        
#         return output_df
    
#     def process(self):
#         """Main processing pipeline"""
#         print("\n" + "="*60)
#         print("MEMES DATASET PROCESSING PIPELINE")
#         print("="*60)
        
#         # Step 1: Load and merge
#         if not self.load_and_merge_files():
#             logger.error("No files to process!")
#             return None
        
#         # Step 2: Initial overview
#         self.dataset_overview("BEFORE CLEANING")
        
#         # Step 3: Clean column names
#         self.clean_column_names()
        
#         # Step 4: Safely fill columns
#         self.safe_fill_columns()
        
#         # Step 5: Drop useless columns
#         self.drop_useless_columns()
        
#         # Step 6: Create final text
#         self.create_final_text()
        
#         # Step 7: Remove noise
#         self.remove_noise()
        
#         # Step 8: Extract metadata
#         self.extract_metadata()
        
#         # Step 9: Add analysis columns
#         self.add_analysis_columns()
        
#         # Step 10: Final overview
#         print("\n" + "="*60)
#         self.dataset_overview("AFTER CLEANING")
        
#         return self.df

# def main():
#     # Configuration
#     input_path = r"F:\Project\Memes\*.csv"
#     output_path = r"F:\Project\Memes\processed_memes.csv"
    
#     # Process memes
#     processor = MemesDatasetProcessor(input_path)
#     processed_df = processor.process()
    
#     if processed_df is not None:
#         # Save results
#         processor.save_processed_data(output_path)
        
#         # Show sample
#         print("\n📝 Sample Records (first 5):")
#         print("-" * 60)
#         sample_cols = ['final_text', 'platform', 'subject', 'topic']
#         sample_cols = [col for col in sample_cols if col in processed_df.columns]
#         print(processed_df[sample_cols].head(10).to_string())
        
#         print("\n✅ Processing complete!")
#     else:
#         print("\n❌ Processing failed!")

# if __name__ == "__main__":
#     main()
# ---------------------------------------------


import pandas as pd

df = pd.read_csv(
    r"F:\Project\Memes\memes_cleaned.csv",
    dtype=str
)

print(df['final_text'].head(10))
print(df['final_text'].isna().sum())
# Convert everything to string & strip spaces
df['final_text'] = df['final_text'].astype(str).str.strip()

# Remove invalid text rows
df = df[
    (df['final_text'] != '') &
    (df['final_text'].str.lower() != 'nan') &
    (df['final_text'].notna())
]
# Convert everything to string & strip spaces
df['final_text'] = df['final_text'].astype(str).str.strip()

# Remove invalid text rows
df = df[
    (df['final_text'] != '') &
    (df['final_text'].str.lower() != 'nan') &
    (df['final_text'].notna())
]
df.drop(columns=['thumbnail'], inplace=True, errors='ignore')
df = df.where(pd.notnull(df), None)
output_path = r"F:\Project\Memes\memes_cleaned_FINAL.csv"
df.to_csv(output_path, index=False)

print("✅ Final cleaned CSV saved:", output_path)
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])
