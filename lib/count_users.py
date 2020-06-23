trl_profile = [5, 6, 8, 8, 8, 5, 3, 1, 1, 1, 1, 1, 1, 1]  # 0: today, 1: yesterday, ...


def count_users(diagnosis_key_list):
    print("Parsing the Diagnosis Key list, counting unique users...")
    print("Length: %d keys (%d without padding)" % (len(diagnosis_key_list), len(diagnosis_key_list) // 10))
    if len(diagnosis_key_list) % 10 != 0:
        print("WARNING: Apparently the list is not padded by 10!")
    latest_interval = max(dk.start_interval for dk in diagnosis_key_list)

    user_days = []

    num_old_android_apps = 0
    top_level_dks = [dk for dk in diagnosis_key_list if dk.start_interval == latest_interval]
    for dk in top_level_dks:
        try:
            pos = trl_profile[2:].index(dk.transmission_risk_level)+2
        except ValueError:
            continue
        diagnosis_key_list.remove(dk)
        days = 1
        interval = latest_interval
        while pos > 1:
            interval -= 144
            next_dk = next((dk_entry for dk_entry in diagnosis_key_list
                            if (dk_entry.start_interval == interval) and
                            (dk_entry.transmission_risk_level == trl_profile[pos-1])), None)
            if (next_dk is None) and (trl_profile[pos] == 8):
                pos += 1
                next_dk = next((dk_entry for dk_entry in diagnosis_key_list
                                if (dk_entry.start_interval == interval) and
                                (dk_entry.transmission_risk_level == trl_profile[pos - 1])), None)
            if next_dk is None:
                break
            diagnosis_key_list.remove(next_dk)
            days += 1
            pos -= 1
        user_days.append(days)
        num_old_android_apps += 1

    top_level_dks = [dk for dk in diagnosis_key_list if dk.start_interval == latest_interval]
    for dk in top_level_dks:
        days = 0
        if dk.transmission_risk_level == trl_profile[1]:  # newest entry is from yesterday
            diagnosis_key_list.remove(dk)
            days = 1
            interval = latest_interval
            while days < len(trl_profile):
                interval -= 144
                next_dk = next((dk_entry for dk_entry in diagnosis_key_list
                                if (dk_entry.start_interval == interval) and
                                (dk_entry.transmission_risk_level == trl_profile[days+1])), None)
                if next_dk is None:
                    break
                diagnosis_key_list.remove(next_dk)
                days += 1
        user_days.append(days)


    reduced_users = len(user_days) // 10
    print("%d user(s) found." % reduced_users)

    days_count = [0] * 15
    for entry in user_days:
        days_count[entry] += 1
    reduced_days_count = [days // 10 for days in days_count]
    print("They submitted these numbers of keys:")
    days = 0
    for count in reduced_days_count:
        if count > 0:
            if days > 0:
                print("%d user(s): %d Diagnosis Key(s)" % (count, days))
            else:
                print("%d user(s): Invalid Transmission Risk Profile" % count)
        days += 1

    if num_old_android_apps > 0:
        print("Old Android app used by %d user(s)." % (num_old_android_apps // 10))
    print("%d keys not parsed (%d without padding)." % (len(diagnosis_key_list), len(diagnosis_key_list) // 10))
