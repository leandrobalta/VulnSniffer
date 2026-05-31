import os
import pandas as pd

def generate_stratified_sample(input_path, output_path, sample_percentage=10):
    """
    Selects a random percentage of records strictly for 'CORRETO' and 'INCORRETO'
    statuses, completely ignoring any other classifications.
    """
    if not os.path.exists(input_path):
        print(f"❌ Error: The file '{input_path}' was not found.")
        return

    # 1. Load the original audit CSV file
    df = pd.read_csv(input_path)
    
    # Clean whitespaces from column names and Status string values
    df.columns = df.columns.str.strip()
    if 'Status' in df.columns:
        df['Status'] = df['Status'].str.strip()

    # 2. Strictly filter the categories of interest (Ignore NAO_SE_APLICA)
    df_filtered = df[df['Status'].isin(['CORRETO', 'INCORRETO'])].copy()

    if df_filtered.empty:
        print("⚠️ Warning: No records found with 'CORRETO' or 'INCORRETO' status.")
        return

    # 3. Perform stratified sampling based on 'Status'
    fraction = sample_percentage / 100.0
    
    # Group by 'Status' and sample the fraction independently from each group
    # random_state=42 ensures the scientific reproducibility of the sample extraction
    df_sample = df_filtered.groupby('Status', group_keys=False).apply(
        lambda x: x.sample(frac=fraction, random_state=42)
    )

    # 4. Save the sampled results into a new CSV file
    df_sample.to_csv(output_path, index=False)
    
    # Display sampling metrics and validation in the terminal
    print("=" * 60)
    print(f"✨ Restricted Sampling of {sample_percentage}% completed successfully!")
    print("=" * 60)
    print(f"📁 File saved to: {output_path}")
    print(f"📊 Total records extracted for the expert: {len(df_sample)}")
    print("\nCategory distribution in the final sample:")
    
    counts = df_sample['Status'].value_counts()
    for category, total in counts.items():
        print(f"  - {category}: {total} repositories")
    print("=" * 60)

if __name__ == "__main__":
    # Define input and output file paths
    INPUT_FILE = "../csv/results_audit.csv"
    OUTPUT_FILE = "../csv/results_audit_sample.csv"

    # 🎯 Adjust the target percentage here (e.g., 10 for 10%)
    PERCENTAGE = 10 
    
    generate_stratified_sample(INPUT_FILE, OUTPUT_FILE, sample_percentage=PERCENTAGE)