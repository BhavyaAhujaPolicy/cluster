from advanced_time_analysis import advanced_analyze_time_slots, generate_advanced_insights, calculate_cluster_quality_score
from itertools import combinations
import pandas as pd
import numpy as np

CLUSTER_FIELDS = [
    ('AgeGroup', 'AgeGroup'),
    ('IncomeGroup', 'IncomeGroup'),
    ('Gender', 'Gender'),
    ('ProfessionType', 'Profession'),
    ('Brandname', 'Brand'),
    ('CityId', 'CityId'),
]

MIN_CLUSTER_SIZE = 6000

def calculate_success_probability(group):
    """
    Calculate the probability of successful calls for a cluster.
    """
    if len(group) < 10:
        return 0
    
    # Base success rate from pickup rate
    avg_pickup = group['PickupRate'].mean() if 'PickupRate' in group.columns else 0
    
    # Duration factor (longer calls = better leads)
    avg_duration = group['CallDuration'].mean() if 'CallDuration' in group.columns else 0
    duration_factor = min(avg_duration / 300, 1.0)
    
    # Consistency factor (stable performance)
    pickup_std = group['PickupRate'].std() if 'PickupRate' in group.columns else 0
    consistency_factor = 1 - (pickup_std / avg_pickup) if avg_pickup > 0 else 0
    
    # Sample size factor (more data = more reliable)
    sample_factor = min(len(group) / 1000, 1.0)
    
    # Combined success probability
    success_prob = (avg_pickup / 100) * duration_factor * consistency_factor * sample_factor * 100
    
    return round(success_prob, 2)

def analyze_call_volume_patterns(group):
    """
    Analyze optimal call volume recommendations for a cluster.
    """
    if 'TotalCalls' not in group.columns:
        return {}
    
    patterns = {}
    
    # Daily call volume patterns
    if 'Day' in group.columns:
        daily_volume = group.groupby('Day')['TotalCalls'].sum()
        patterns['avg_daily_calls'] = daily_volume.mean()
        patterns['peak_day'] = daily_volume.idxmax() if not daily_volume.empty else None
    
    # Hourly call volume patterns
    if 'Hour' in group.columns:
        hourly_volume = group.groupby('Hour')['TotalCalls'].sum()
        patterns['avg_hourly_calls'] = hourly_volume.mean()
        patterns['peak_hour'] = hourly_volume.idxmax() if not hourly_volume.empty else None
    
    # Recommended call frequency
    if 'PickupRate' in group.columns:
        avg_pickup = group['PickupRate'].mean()
        if avg_pickup > 50:
            patterns['recommended_frequency'] = 'High (3-5 calls/day)'
        elif avg_pickup > 30:
            patterns['recommended_frequency'] = 'Medium (2-3 calls/day)'
        else:
            patterns['recommended_frequency'] = 'Low (1-2 calls/day)'
    
    return patterns

def calculate_predictive_score(group):
    """
    Calculate a predictive score for future call success.
    """
    if len(group) < 10:
        return 0
    
    # Base score from current performance
    base_score = calculate_success_probability(group)
    
    # Trend factor (if improving, higher score)
    if 'PickupRate' in group.columns:
        recent_pickup = group['PickupRate'].tail(100).mean() if len(group) >= 100 else group['PickupRate'].mean()
        overall_pickup = group['PickupRate'].mean()
        trend_factor = 1.2 if recent_pickup > overall_pickup else 0.8
    else:
        trend_factor = 1.0
    
    # Consistency factor
    if 'PickupRate' in group.columns:
        pickup_std = group['PickupRate'].std()
        pickup_mean = group['PickupRate'].mean()
        consistency_factor = 1 - (pickup_std / pickup_mean) if pickup_mean > 0 else 0.5
    else:
        consistency_factor = 0.5
    
    # Sample size factor
    sample_factor = min(len(group) / 1000, 1.0)
    
    # Final predictive score
    predictive_score = base_score * trend_factor * consistency_factor * sample_factor
    
    return round(predictive_score, 2)

def advanced_generate_clusters(df):
    """
    Advanced clustering with quality metrics and predictive scoring.
    """
    # Only use rows with all required columns
    required = [col for col, _ in CLUSTER_FIELDS]
    df = df.dropna(subset=required)
    df = df.copy()
    clusters = []
    
    # Always group by AgeGroup and IncomeGroup first (not grouped together)
    grouped_primary = df.groupby(['AgeGroup', 'IncomeGroup'])
    
    for (age_group, income_group), primary_group in grouped_primary:
        # Try all combinations of other fields (from most to least)
        other_fields = [f for f in CLUSTER_FIELDS if f[0] not in ['AgeGroup', 'IncomeGroup']]
        
        for level in range(len(other_fields), 0, -1):
            combos = list(combinations(other_fields, level))
            found = False
            
            for field_combo in combos:
                groupby_fields = [col for col, _ in field_combo]
                output_keys = [out for _, out in field_combo]
                grouped = primary_group.groupby(groupby_fields)
                
                for keys, group in grouped:
                    if len(group) >= MIN_CLUSTER_SIZE:
                        # Basic cluster info
                        cluster = {
                            'AgeGroup': age_group,
                            'IncomeGroup': income_group
                        }
                        
                        # Set other fields (comma-joined)
                        for i, out_key in enumerate(output_keys):
                            vals = group[groupby_fields[i]].dropna().unique()
                            cluster[out_key] = ','.join(sorted(map(str, vals)))
                        
                        # Advanced metrics
                        cluster['LeadCount'] = len(group)
                        cluster['ClusterQuality'] = calculate_cluster_quality_score(group)
                        cluster['SuccessProbability'] = calculate_success_probability(group)
                        cluster['PredictiveScore'] = calculate_predictive_score(group)
                        
                        # Call volume patterns
                        volume_patterns = analyze_call_volume_patterns(group)
                        cluster.update(volume_patterns)
                        
                        # Advanced insights
                        advanced_insights = generate_advanced_insights(group)
                        cluster.update(advanced_insights)
                        
                        # Advanced time analysis
                        cluster['AdvancedPickupPattern'] = advanced_analyze_time_slots(group)
                        
                        clusters.append(cluster)
                        found = True
                
                if found:
                    break  # Only use the most granular grouping possible
            if found:
                break
    
    return clusters

def generate_cluster_recommendations(clusters):
    """
    Generate actionable recommendations for each cluster.
    """
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
    
    return recommendations 