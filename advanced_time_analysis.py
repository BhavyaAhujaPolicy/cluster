import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict

def calculate_confidence(sample_size, pickup_rate, duration, consistency_score):
    """
    Calculate confidence score for time slots based on multiple factors.
    """
    # Sample size weight (0-1)
    sample_weight = min(sample_size / 100, 1.0)
    
    # Pickup rate weight (higher is better, but not too high)
    pickup_weight = min(pickup_rate / 50, 1.0)
    
    # Duration weight (longer calls are better)
    duration_weight = min(duration / 300, 1.0)
    
    # Consistency weight (how stable the metrics are)
    consistency_weight = consistency_score
    
    # Combined confidence score (0-100)
    confidence = (sample_weight * 0.3 + 
                 pickup_weight * 0.3 + 
                 duration_weight * 0.2 + 
                 consistency_weight * 0.2) * 100
    
    return round(confidence, 2)

def analyze_behavioral_patterns(group):
    """
    Analyze behavioral patterns within a cluster.
    """
    patterns = {}
    
    if 'PickupRate' in group.columns and 'CallDuration' in group.columns:
        # Response time patterns (how quickly people pick up)
        patterns['avg_response_time'] = group['PickupRate'].mean()
        patterns['response_consistency'] = group['PickupRate'].std()
        
        # Call duration patterns
        patterns['avg_duration'] = group['CallDuration'].mean()
        patterns['duration_consistency'] = group['CallDuration'].std()
        
        # Call frequency patterns (if available)
        if 'TotalCalls' in group.columns:
            patterns['call_frequency'] = group['TotalCalls'].sum()
    
    return patterns

def analyze_trends(group, days_back=30):
    """
    Analyze trends in pickup rates and duration over time.
    """
    if 'Day' not in group.columns:
        return {}
    
    # Convert to datetime for trend analysis
    group['Date'] = pd.to_datetime(group['Day'], errors='coerce')
    recent_data = group[group['Date'] >= (datetime.now() - timedelta(days=days_back))]
    
    if len(recent_data) < 10:
        return {}
    
    # Calculate trends
    trends = {}
    
    # Pickup rate trend
    if 'PickupRate' in recent_data.columns:
        pickup_trend = np.polyfit(range(len(recent_data)), recent_data['PickupRate'], 1)[0]
        trends['pickup_trend'] = 'improving' if pickup_trend > 0 else 'declining'
        trends['pickup_trend_score'] = abs(pickup_trend)
    
    # Duration trend
    if 'CallDuration' in recent_data.columns:
        duration_trend = np.polyfit(range(len(recent_data)), recent_data['CallDuration'], 1)[0]
        trends['duration_trend'] = 'improving' if duration_trend > 0 else 'declining'
        trends['duration_trend_score'] = abs(duration_trend)
    
    return trends

def advanced_analyze_time_slots(group, pickup_threshold=3, duration_threshold=30, min_samples=50):
    """
    Advanced time slot analysis with confidence scoring and behavioral patterns.
    """
    result = []

    if 'Day' not in group.columns or 'Hour' not in group.columns:
        return result

    group = group.copy()
    group['Hour'] = group['Hour'].astype(int)
    
    
    # Analyze behavioral patterns
    behavioral_patterns = analyze_behavioral_patterns(group)
    
    # Analyze trends
    trends = analyze_trends(group)

    for day, day_df in group.groupby('Day'):
        hourly = day_df.groupby('Hour').agg(
            PickupRate=('PickupRate', 'mean'),
            AvgDuration=('CallDuration', 'mean'),
            SampleSize=('PickupRate', 'count'),
            PickupStd=('PickupRate', 'std'),
            DurationStd=('CallDuration', 'std')
        ).reset_index()

        hourly = hourly[hourly['SampleSize'] >= min_samples]
        if hourly.empty:
            continue

        merged_ranges = []
        current = {'start': None, 'end': None, 'pickup': [], 'duration': [], 'samples': []}

        for _, row in hourly.iterrows():
            hr = row['Hour']
            pr, dur, samples = row['PickupRate'], row['AvgDuration'], row['SampleSize']

            if current['start'] is None:
                current.update({'start': hr, 'end': hr, 'pickup': [pr], 'duration': [dur], 'samples': [samples]})
            elif abs(pr - current['pickup'][-1]) <= pickup_threshold and abs(dur - current['duration'][-1]) <= duration_threshold:
                current['end'] = hr
                current['pickup'].append(pr)
                current['duration'].append(dur)
                current['samples'].append(samples)
            else:
                merged_ranges.append(current)
                current = {'start': hr, 'end': hr, 'pickup': [pr], 'duration': [dur], 'samples': [samples]}

        if current['start'] is not None:
            merged_ranges.append(current)

        for r in merged_ranges:
            avg_pickup = sum(r['pickup']) / len(r['pickup'])
            avg_duration = sum(r['duration']) / len(r['duration'])
            total_samples = sum(r['samples'])
            
            # Calculate consistency score
            pickup_consistency = 1 - (np.std(r['pickup']) / avg_pickup) if avg_pickup > 0 else 0
            duration_consistency = 1 - (np.std(r['duration']) / avg_duration) if avg_duration > 0 else 0
            consistency_score = (pickup_consistency + duration_consistency) / 2
            
            # Calculate confidence
            confidence = calculate_confidence(total_samples, avg_pickup, avg_duration, consistency_score)
            
            # Calculate success probability
            success_probability = min((avg_pickup / 100) * (avg_duration / 300) * 100, 100)
            
            result.append({
                'Day': day,
                'Time': f"{int(r['start']):02d}:00–{int(r['end'])+1:02d}:00",
                'PickupRate': round(avg_pickup, 2),
                'AvgDuration': round(avg_duration, 2),
                'SampleSize': total_samples,
                'Confidence': confidence,
                'SuccessProbability': round(success_probability, 2),
                'ConsistencyScore': round(consistency_score, 2),
                'BestTime': False,
                'BehavioralPatterns': behavioral_patterns,
                'Trends': trends
            })

    # Sort by success probability and confidence
    result.sort(key=lambda x: (x['SuccessProbability'], x['Confidence']), reverse=True)
    
    # Mark top 3 as best times
    for i in range(min(3, len(result))):
        result[i]['BestTime'] = True

    return result

def calculate_cluster_quality_score(group):
    """
    Calculate how well-defined and homogeneous a cluster is.
    """
    if len(group) < 10:
        return 0
    
    # Age group homogeneity
    age_homogeneity = 1 - (group['AgeGroup'].nunique() / len(group)) if 'AgeGroup' in group.columns else 0
    
    # Income homogeneity
    income_homogeneity = 1 - (group['IncomeGroup'].nunique() / len(group)) if 'IncomeGroup' in group.columns else 0
    
    # Geographic homogeneity
    geo_homogeneity = 1 - (group['CityName'].nunique() / len(group)) if 'CityName' in group.columns else 0
    
    # Overall quality score
    quality_score = (age_homogeneity + income_homogeneity + geo_homogeneity) / 3 * 100
    
    return round(quality_score, 2)

def generate_advanced_insights(group):
    """
    Generate advanced insights for a cluster.
    """
    insights = {}
    
    # Cluster quality
    insights['cluster_quality'] = calculate_cluster_quality_score(group)
    
    # Behavioral analysis
    behavioral = analyze_behavioral_patterns(group)
    insights.update(behavioral)
    
    # Trend analysis
    trends = analyze_trends(group)
    insights.update(trends)
    
    # Geographic performance
    if 'CityName' in group.columns and 'PickupRate' in group.columns:
        city_performance = group.groupby('CityName')['PickupRate'].mean().to_dict()
        insights['city_performance'] = city_performance
    
    return insights 