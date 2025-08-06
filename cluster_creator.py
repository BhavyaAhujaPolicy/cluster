from time_analysis import analyze_time_slots
from itertools import combinations

CLUSTER_FIELDS = [
    ('AgeGroup', 'AgeGroup'),
    ('Gender', 'Gender'),
    ('IncomeGroup', 'IncomeGroup'),
    ('ProfessionType', 'Profession'),
    ('CityId', 'City'),
    ('Brandname', 'Brand'),
]

MIN_CLUSTER_SIZE = 6000

def generate_clusters(df):
    # ✅ Skip invalid ages only
    if 'Age' in df.columns:
        df = df[(df['Age'] >= 18) & (df['Age'] <= 87)].copy()

    df = df.copy()
    df["assigned"] = False
    clusters = []

    available_fields = [(col, out) for col, out in CLUSTER_FIELDS if col in df.columns]
    if not available_fields:
        raise ValueError("No valid fields for clustering.")

    for level in range(len(available_fields), 0, -1):
        combos = list(combinations(available_fields, level))

        for field_combo in combos:
            groupby_fields = [col for col, _ in field_combo]
            output_keys = [out for _, out in field_combo]
            sub_df = df[~df["assigned"]].copy()

            grouped = sub_df.groupby(groupby_fields)

            for keys, group in grouped:
                if len(group) >= MIN_CLUSTER_SIZE:
                    cluster = {}
                    for i, out_key in enumerate(output_keys):
                        if out_key == 'City':
                            if 'CityId' in group.columns:
                                cities = group['CityId'].dropna().unique()
                                cluster['City'] = ", ".join(sorted(map(str, cities))) if len(cities) > 0 else ''
                            else:
                                cluster['City'] = ''
                        elif out_key == 'Profession':
                            if 'ProfessionType' in group.columns:
                                profs = group['ProfessionType'].dropna().unique()
                                cluster['Profession'] = ", ".join(sorted(map(str, profs))) if len(profs) > 0 else ''
                            else:
                                cluster['Profession'] = ''
                        else:
                            if groupby_fields[i] in group.columns:
                                val = group[groupby_fields[i]].dropna().unique()
                                cluster[out_key] = ", ".join(sorted(map(str, val))) if len(val) > 0 else ''
                            else:
                                cluster[out_key] = ''
                    if 'Brandname' in group.columns:
                        brands = group['Brandname'].dropna().unique()
                        cluster['Brand'] = ", ".join(sorted(map(str, brands))) if len(brands) > 0 else ''
                    else:
                        cluster['Brand'] = ''
                    cluster["LeadCount"] = len(group)
                    cluster["PickupPattern"] = analyze_time_slots(group)
                    # Only one value for AgeGroup and IncomeGroup
                    if 'AgeGroup' in group.columns:
                        vals = group['AgeGroup'].dropna().unique()
                        cluster['AgeGroup'] = ", ".join(sorted(map(str, vals))) if len(vals) > 0 else ''
                    if 'IncomeGroup' in group.columns:
                        vals = group['IncomeGroup'].dropna().unique()
                        cluster['IncomeGroup'] = ", ".join(sorted(map(str, vals))) if len(vals) > 0 else ''
                    clusters.append(cluster)
                    df.loc[group.index, "assigned"] = True

        remaining = len(df[~df["assigned"]])
        print(f"✅ Clusters formed with {level} fields: {len(clusters)} | Unassigned rows: {remaining}")
        if remaining == 0:
            break

    # Handle leftover rows directly (no merging logic)
    leftover_df = df[~df["assigned"]]
    if not leftover_df.empty:
        cluster = {"MergedFrom": "Leftovers", "LeadCount": len(leftover_df)}
        if 'CityId' in leftover_df.columns:
            cities = leftover_df['CityId'].dropna().unique()
            cluster['City'] = ", ".join(sorted(map(str, cities))) if len(cities) > 0 else ''
        if 'ProfessionType' in leftover_df.columns:
            profs = leftover_df['ProfessionType'].dropna().unique()
            cluster['Profession'] = ", ".join(sorted(map(str, profs))) if len(profs) > 0 else ''
        if 'AgeGroup' in leftover_df.columns:
            vals = leftover_df['AgeGroup'].dropna().unique()
            cluster['AgeGroup'] = ", ".join(sorted(map(str, vals))) if len(vals) > 0 else ''
        if 'IncomeGroup' in leftover_df.columns:
            vals = leftover_df['IncomeGroup'].dropna().unique()
            cluster['IncomeGroup'] = ", ".join(sorted(map(str, vals))) if len(vals) > 0 else ''
        if 'Brandname' in leftover_df.columns:
            brands = leftover_df['Brandname'].dropna().unique()
            cluster['Brand'] = ", ".join(sorted(map(str, brands))) if len(brands) > 0 else ''
        cluster["PickupPattern"] = analyze_time_slots(leftover_df)
        clusters.append(cluster)

    return clusters
