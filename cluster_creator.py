import json
from time_analysis import analyze_time_slots
from itertools import combinations

CLUSTER_FIELDS = [
    ('AgeGroup', 'AgeGroup'),
    ('IncomeGroup', 'IncomeGroup'),
    ('Gender', 'Gender'),
    ('ProfessionType', 'Profession'),
    ('Brandname', 'Brand'),
    ('CityId', 'CityId'),
    ('CityName', 'CityName'),
]

MIN_CLUSTER_SIZE = 6000

def generate_clusters(df):
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
                        cluster = {
                            'AgeGroup': age_group,
                            'IncomeGroup': income_group
                        }
                        # Set other fields (comma-joined)
                        for i, out_key in enumerate(output_keys):
                            vals = group[groupby_fields[i]].dropna().unique()
                            cluster[out_key] = ','.join(sorted(map(str, vals)))
                        # Lead count
                        cluster['LeadCount'] = len(group)
                        # Pickup pattern
                        cluster['PickupPattern'] = analyze_time_slots(group)
                        clusters.append(cluster)
                        found = True
                if found:
                    break  # Only use the most granular grouping possible
            if found:
                break
    return clusters
