from data_loader import load_data, preprocess, stream_json_chunks
from cluster_creator import generate_clusters
from export_excel import export_to_excel
from advanced_cluster_creator import advanced_generate_clusters
from advanced_export_excel import export_advanced_clusters_to_excel, export_comparison_report
from config import DATA_PATH
import pandas as pd
import sys
from tqdm import tqdm

def run_original_pipeline():
    """
    Run the original clustering pipeline.
    """
    print("🔄 Running ORIGINAL clustering pipeline...")
    print("📊 Loading data...")
    
    total_rows = 1310000
    chunk_size = 100000
    dfs = []
    
    try:
        for df_chunk in tqdm(stream_json_chunks(DATA_PATH, chunk_size=chunk_size, total_rows=total_rows), 
                            desc="Loading JSON"):
            dfs.append(df_chunk)
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted! Proceeding with loaded data so far...")
    
    if not dfs:
        print("❌ No data loaded. Exiting.")
        return None
    
    df = pd.concat(dfs, ignore_index=True)
    print(f"✅ Loaded {len(df):,} rows")
    
    print("🔍 Generating clusters...")
    original_clusters = generate_clusters(df)
    print(f"✅ Generated {len(original_clusters)} original clusters")
    
    print("📤 Exporting original results...")
    export_to_excel(original_clusters, "output_original_clusters.xlsx")
    print("✅ Original results saved to 'output_original_clusters.xlsx'")
    
    return original_clusters

def run_advanced_pipeline():
    """
    Run the advanced clustering pipeline with all enhancements.
    """
    print("\n🚀 Running ADVANCED clustering pipeline...")
    print("📊 Loading data...")
    
    total_rows = 1310000
    chunk_size = 100000
    dfs = []
    
    try:
        for df_chunk in tqdm(stream_json_chunks(DATA_PATH, chunk_size=chunk_size, total_rows=total_rows), 
                            desc="Loading JSON"):
            dfs.append(df_chunk)
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted! Proceeding with loaded data so far...")
    
    if not dfs:
        print("❌ No data loaded. Exiting.")
        return None
    
    df = pd.concat(dfs, ignore_index=True)
    print(f"✅ Loaded {len(df):,} rows")
    
    print("🔍 Generating advanced clusters...")
    advanced_clusters = advanced_generate_clusters(df)
    print(f"✅ Generated {len(advanced_clusters)} advanced clusters")
    
    print("📤 Exporting advanced results...")
    export_advanced_clusters_to_excel(advanced_clusters, "output_advanced_clusters.xlsx")
    print("✅ Advanced results saved to 'output_advanced_clusters.xlsx'")
    
    return advanced_clusters

def generate_comparison_report(original_clusters, advanced_clusters):
    """
    Generate comparison report between original and advanced results.
    """
    print("\n📊 Generating comparison report...")
    
    if original_clusters and advanced_clusters:
        export_comparison_report(original_clusters, advanced_clusters, "comparison_report.xlsx")
        print("✅ Comparison report saved to 'comparison_report.xlsx'")
        
        # Print summary
        print("\n📈 COMPARISON SUMMARY:")
        print(f"Original clusters: {len(original_clusters)}")
        print(f"Advanced clusters: {len(advanced_clusters)}")
        
        # Calculate average metrics
        if advanced_clusters:
            avg_success = sum(c.get('SuccessProbability', 0) for c in advanced_clusters) / len(advanced_clusters)
            avg_quality = sum(c.get('ClusterQuality', 0) for c in advanced_clusters) / len(advanced_clusters)
            print(f"Average Success Probability: {avg_success:.2f}%")
            print(f"Average Cluster Quality: {avg_quality:.2f}%")
    
    print("\n🎯 ANALYSIS COMPLETE!")
    print("📁 Files generated:")
    print("  - output_original_clusters.xlsx (Original results)")
    print("  - output_advanced_clusters.xlsx (Advanced results)")
    print("  - comparison_report.xlsx (Comparison analysis)")

def main():
    """
    Main function to run both pipelines and generate comparison.
    """
    print("🎯 TELE-CALLING CLUSTER ANALYSIS")
    print("=" * 50)
    
    # Run original pipeline
    original_clusters = run_original_pipeline()
    
    # Run advanced pipeline
    advanced_clusters = run_advanced_pipeline()
    
    # Generate comparison
    generate_comparison_report(original_clusters, advanced_clusters)
    
    print("\n🎉 Both pipelines completed successfully!")
    print("📊 You can now compare the results in the generated Excel files.")

if __name__ == "__main__":
    main() 