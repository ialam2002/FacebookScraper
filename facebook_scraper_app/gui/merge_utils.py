# Utility to merge multiple profiles into a single primary profile with deduplicated friends

def merge_profiles(network_data, person_to_profiles=None):
    """
    Merge profiles by person group.
    network_data: dict of profile_url -> data
    person_to_profiles: dict of person_id (e.g. name) -> list of profile_urls
    Returns: dict of person_id -> merged profile data (primary profile + all deduped friends)
    """
    if not network_data:
        return {}

    if not person_to_profiles:
        # Fallback: treat all as one group (old behavior)
        profiles = list(network_data.items())
        primary_url, primary_data = max(profiles, key=lambda x: len(x[1].get('friends', [])))
        all_friends = []
        for url, data in profiles:
            all_friends.extend(data.get('friends', []))
        seen = set()
        deduped_friends = []
        for friend in all_friends:
            key = friend.get('url') or friend.get('name')
            if key and key not in seen:
                deduped_friends.append(friend)
                seen.add(key)
        merged = {
            primary_url: {
                **primary_data,
                'friends': deduped_friends
            }
        }
        return merged

    merged = {}
    for person_id, profile_urls in person_to_profiles.items():
        # Only use profiles that exist in network_data
        profiles = [(url, network_data[url]) for url in profile_urls if url in network_data]
        if not profiles:
            continue
        primary_url, primary_data = max(profiles, key=lambda x: len(x[1].get('friends', [])))
        all_friends = []
        for url, data in profiles:
            all_friends.extend(data.get('friends', []))
        seen = set()
        deduped_friends = []
        for friend in all_friends:
            key = friend.get('url') or friend.get('name')
            if key and key not in seen:
                deduped_friends.append(friend)
                seen.add(key)
        # Ensure profile_name is not empty
        profile_name = primary_data.get('profile_name', '')
        if not profile_name:
            for _, data in profiles:
                if data.get('profile_name'):
                    profile_name = data['profile_name']
                    break
        if not profile_name:
            profile_name = person_id
        merged[person_id] = {
            **primary_data,
            'profile_name': profile_name,
            'friends': deduped_friends,
            'profile_urls': profile_urls,
            'person_id': person_id
        }
    return merged
