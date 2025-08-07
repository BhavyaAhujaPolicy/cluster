import pandas as pd
import json

def export_advanced_clusters_to_excel(clusters, filename="output_advanced_clusters.xlsx"):
    """
    Export advanced clusters with all new metrics and insights.
    """
    rows = []

    for idx, cluster in enumerate(clusters, start=1):
        # Basic cluster info
        cluster_base = {
            'ClusterIndex': idx,
            'AgeGroup': cluster.get('AgeGroup', ''),
            'IncomeGroup': cluster.get('IncomeGroup', ''),
            'Gender': cluster.get('Gender', ''),
            'Profession': cluster.get('Profession', ''),
            'Brand': cluster.get('Brand', ''),
            'CityId': cluster.get('CityId', ''),
            'CityName': cluster.get('CityName', ''),
            'LeadCount': cluster.get('LeadCount', 0),
            
            # Advanced metrics
            'ClusterQuality': cluster.get('ClusterQuality', 0),
            'SuccessProbability': cluster.get('SuccessProbability', 0),
            'PredictiveScore': cluster.get('PredictiveScore', 0),
            
            # Call volume patterns
            'AvgDailyCalls': cluster.get('avg_daily_calls', 0),
            'PeakDay': cluster.get('peak_day', ''),
            'AvgHourlyCalls': cluster.get('avg_hourly_calls', 0),
            'PeakHour': cluster.get('peak_hour', ''),
            'RecommendedFrequency': cluster.get('recommended_frequency', ''),
            
            # Behavioral patterns
            'AvgResponseTime': cluster.get('avg_response_time', 0),
            'ResponseConsistency': cluster.get('response_consistency', 0),
            'AvgDuration': cluster.get('avg_duration', 0),
            'DurationConsistency': cluster.get('duration_consistency', 0),
            'CallFrequency': cluster.get('call_frequency', 0),
            
            # Trend analysis
            'PickupTrend': cluster.get('pickup_trend', ''),
            'PickupTrendScore': cluster.get('pickup_trend_score', 0),
            'DurationTrend': cluster.get('duration_trend', ''),
            'DurationTrendScore': cluster.get('duration_trend_score', 0),
        }

        # Advanced time patterns
        advanced_pattern = cluster.get("AdvancedPickupPattern", [])

        if not advanced_pattern:
            row = cluster_base.copy()
            row.update({
                'Day': '',
                'Time': '',
                'PickupRate': '',
                'AvgDuration': '',
                'SampleSize': '',
                'Confidence': '',
                'SuccessProbability_Time': '',
                'ConsistencyScore': '',
                'BestTime': False
            })
            rows.append(row)
        else:
            for p in advanced_pattern:
                row = cluster_base.copy()
                row.update({
                    'Day': p.get('Day', ''),
                    'Time': p.get('Time', ''),
                    'PickupRate': p.get('PickupRate', ''),
                    'AvgDuration': p.get('AvgDuration', ''),
                    'SampleSize': p.get('SampleSize', ''),
                    'Confidence': p.get('Confidence', ''),
                    'SuccessProbability_Time': p.get('SuccessProbability', ''),
                    'ConsistencyScore': p.get('ConsistencyScore', ''),
                    'BestTime': p.get('BestTime', False)
                })
                rows.append(row)

    # Create main clusters DataFrame
    df_clusters = pd.DataFrame(rows)
    
    # Create recommendations DataFrame
    recommendations = []
    for cluster in clusters:
        rec = {
            'ClusterIndex': len(recommendations) + 1,
            'AgeGroup': cluster.get('AgeGroup', ''),
            'IncomeGroup': cluster.get('IncomeGroup', ''),
            'LeadCount': cluster.get('LeadCount', 0),
            'SuccessProbability': cluster.get('SuccessProbability', 0),
            'PredictiveScore': cluster.get('PredictiveScore', 0),
            'ClusterQuality': cluster.get('ClusterQuality', 0),
            'Recommendations': []
        }
        
        # Generate recommendations based on metrics
        if cluster.get('SuccessProbability', 0) > 70:
            rec['Recommendations'].append("High performing cluster - increase call volume")
        elif cluster.get('SuccessProbability', 0) < 30:
            rec['Recommendations'].append("Low performing cluster - optimize timing or reconsider approach")
        
        if cluster.get('PredictiveScore', 0) > cluster.get('SuccessProbability', 0):
            rec['Recommendations'].append("Improving trend - maintain current strategy")
        elif cluster.get('PredictiveScore', 0) < cluster.get('SuccessProbability', 0):
            rec['Recommendations'].append("Declining trend - review and adjust strategy")
        
        if cluster.get('ClusterQuality', 0) > 80:
            rec['Recommendations'].append("Well-defined cluster - highly targeted approach recommended")
        elif cluster.get('ClusterQuality', 0) < 50:
            rec['Recommendations'].append("Heterogeneous cluster - consider sub-segmentation")
        
        # Time-based recommendations
        if 'AdvancedPickupPattern' in cluster:
            best_times = [p for p in cluster['AdvancedPickupPattern'] if p.get('BestTime', False)]
            if best_times:
                rec['Recommendations'].append(f"Focus calls during: {', '.join([t['Time'] for t in best_times[:2]])}")
        
        # Volume recommendations
        if 'recommended_frequency' in cluster:
            rec['Recommendations'].append(f"Call frequency: {cluster['recommended_frequency']}")
        
        recommendations.append(rec)
    
    df_recommendations = pd.DataFrame(recommendations)
    
    # Create summary statistics
    summary_stats = {
        'Metric': [
            'Total Clusters',
            'Average Success Probability',
            'Average Predictive Score',
            'Average Cluster Quality',
            'High Performing Clusters (>70%)',
            'Low Performing Clusters (<30%)',
            'Improving Trends',
            'Declining Trends'
        ],
        'Value': [
            len(clusters),
            round(df_clusters['SuccessProbability'].mean(), 2),
            round(df_clusters['PredictiveScore'].mean(), 2),
            round(df_clusters['ClusterQuality'].mean(), 2),
            len(df_clusters[df_clusters['SuccessProbability'] > 70]),
            len(df_clusters[df_clusters['SuccessProbability'] < 30]),
            len(df_clusters[df_clusters['PredictiveScore'] > df_clusters['SuccessProbability']]),
            len(df_clusters[df_clusters['PredictiveScore'] < df_clusters['SuccessProbability']])
        ]
    }
    
    df_summary = pd.DataFrame(summary_stats)
    
    # Export to Excel with multiple sheets
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df_clusters.to_excel(writer, sheet_name='Advanced_Clusters', index=False)
        df_recommendations.to_excel(writer, sheet_name='Recommendations', index=False)
        df_summary.to_excel(writer, sheet_name='Summary_Statistics', index=False)
        
        # Add insights sheet
        insights_data = []
        for cluster in clusters:
            if 'city_performance' in cluster:
                for city, performance in cluster['city_performance'].items():
                    insights_data.append({
                        'ClusterIndex': cluster.get('AgeGroup', '') + '-' + cluster.get('IncomeGroup', ''),
                        'City': city,
                        'Performance': round(performance, 2),
                        'AgeGroup': cluster.get('AgeGroup', ''),
                        'IncomeGroup': cluster.get('IncomeGroup', '')
                    })
        
        if insights_data:
            df_insights = pd.DataFrame(insights_data)
            df_insights.to_excel(writer, sheet_name='City_Performance', index=False)

def export_comparison_report(original_clusters, advanced_clusters, filename="comparison_report.xlsx"):
    """
    Export a comparison report between original and advanced clustering.
    """
    comparison_data = []
    
    for i, (orig, adv) in enumerate(zip(original_clusters, advanced_clusters)):
        comparison_data.append({
            'ClusterIndex': i + 1,
            'Original_LeadCount': orig.get('LeadCount', 0),
            'Advanced_LeadCount': adv.get('LeadCount', 0),
            'Original_AgeGroup': orig.get('AgeGroup', ''),
            'Advanced_AgeGroup': adv.get('AgeGroup', ''),
            'Original_IncomeGroup': orig.get('IncomeGroup', ''),
            'Advanced_IncomeGroup': adv.get('IncomeGroup', ''),
            'SuccessProbability': adv.get('SuccessProbability', 0),
            'PredictiveScore': adv.get('PredictiveScore', 0),
            'ClusterQuality': adv.get('ClusterQuality', 0),
            'Improvement_Score': round(adv.get('SuccessProbability', 0) - 50, 2)  # Assuming 50% baseline
        })
    
    df_comparison = pd.DataFrame(comparison_data)
    
    # Calculate improvement metrics
    improvement_stats = {
        'Metric': [
            'Total Clusters',
            'Average Success Probability',
            'High Quality Clusters (>80%)',
            'Predictive Accuracy',
            'Overall Improvement'
        ],
        'Value': [
            len(advanced_clusters),
            round(df_comparison['SuccessProbability'].mean(), 2),
            len(df_comparison[df_comparison['ClusterQuality'] > 80]),
            round(df_comparison['PredictiveScore'].mean(), 2),
            round(df_comparison['Improvement_Score'].mean(), 2)
        ]
    }
    
    df_improvement = pd.DataFrame(improvement_stats)
    
    # Export comparison
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df_comparison.to_excel(writer, sheet_name='Cluster_Comparison', index=False)
        df_improvement.to_excel(writer, sheet_name='Improvement_Statistics', index=False) 