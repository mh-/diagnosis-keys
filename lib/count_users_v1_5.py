# Count Users who reported keys using CWA 1.5ff
# see https://github.com/mh-/diagnosis-keys/issues/12
import math
import sys
from lib.conversions import get_datetime_from_utc_timestamp, get_timestamp_from_interval, tek_rolling_period

# TRL Profiles: (0: today, 1: yesterday, ...)  # why 15 values, not 14?
trl_profiles = [[5, 6, 8, 8, 8, 5, 3, 1, 1, 1, 1, 1, 1, 1, 1],  # "classic"
                [5, 6, 7, 7, 7, 6, 4, 3, 2, 1, 1, 1, 1, 1, 1],  # noInformation
                [4, 4, 3, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # nonSymptomatic
                [5, 6, 8, 8, 8, 7, 5, 3, 2, 1, 1, 1, 1, 1, 1],  # symptomaticWithUnknownOnset
                [4, 5, 6, 7, 7, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1],  # lastSevenDays
                [1, 1, 1, 1, 2, 3, 4, 5, 6, 6, 7, 7, 6, 6, 4],  # oneToTwoWeeksAgo
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 3, 4, 5]]  # moreThanTwoWeeksAgo


def count_users(diagnosis_key_list, padding_multiplier=5, auto_multiplier_detect=False):
    print("\nParsing the Diagnosis Key list...")
    original_len = len(diagnosis_key_list)
    if not auto_multiplier_detect:
        print("Length: %d keys (%d without padding)" % (original_len, original_len // padding_multiplier))
        if len(diagnosis_key_list) % padding_multiplier != 0:
            print("WARNING: The number of keys is not a multiple of %d!" % padding_multiplier)
            print("See https://github.com/corona-warn-app/cwa-server/issues/693#issuecomment-672688610",
                  "for a possible explanation.")
    else:
        print("Length: %d keys" % original_len)

    # find min and max start timestamp (interval) in the DK list
    min_interval = sys.maxsize
    max_interval = 0
    for dk in diagnosis_key_list:
        if min_interval > dk.start_interval:
            min_interval = dk.start_interval
        if max_interval < dk.start_interval:
            max_interval = dk.start_interval

    # create a dictionary for each day (also for days that might not have entries in the DK list)
    # key: start_interval, value: a list of 8 counters
    days_dict = dict()
    for interval in range(min_interval, max_interval+1, tek_rolling_period):
        days_dict[interval] = [0, 0, 0, 0, 0, 0, 0, 0]  # number of entries for TRLs from 1 to 8

    # detect padding multiplier
    if auto_multiplier_detect:
        multiplier_candidate_table = [0, 0, 0, 0, 0]  # 1, 2, 3, 4, 5

    # count number of TRLs for each day
    max_value = 0
    for dk in diagnosis_key_list:
        trl_nums = days_dict[dk.start_interval]
        value = trl_nums[dk.transmission_risk_level-1] + 1
        trl_nums[dk.transmission_risk_level-1] = value
        if max_value < value:
            max_value = value
        days_dict[dk.start_interval] = trl_nums

    # print number of TRL for each day
    max_value_width = len("{num}".format(num=max_value))
    trl_sums = [0, 0, 0, 0, 0, 0, 0, 0]
    print("Number of keys per TRL:")
    print("Date:       ", end='')
    for trl in range(8):
        print("{num:{width}}".format(num=trl+1, width=max_value_width + 3), end='')
    print("   Sum:")
    # for each day:
    max_row_sum = 0
    for key in sorted(days_dict.keys(), reverse=True):
        print(get_datetime_from_utc_timestamp(get_timestamp_from_interval(key)).strftime("%Y-%m-%d: "), end='')
        row_sum = 0
        trl = 0
        for trl_num in days_dict[key]:
            print("{num:{width}}".format(num=trl_num, width=max_value_width + 3), end='')
            row_sum += trl_num
            trl += 1
            trl_sums[trl-1] += trl_num
            # detect padding multiplier
            if auto_multiplier_detect:
                for candidate in range(len(multiplier_candidate_table), 0, -1):
                    if trl_num % candidate == 0:
                        multiplier_candidate_table[candidate-1] += 1
                        break
        # print row sum:
        print("  {num:{width}}".format(num=row_sum, width=max_value_width + 2))
        if max_row_sum < row_sum:
            max_row_sum = row_sum

    # print column sum:
    total = 0
    print("Total:      ", end='')
    for row_sum in trl_sums:
        print("{num:{width}}".format(num=row_sum, width=max_value_width + 3), end='')
        total += row_sum
    print("  {num:{width}}".format(num=total, width=max_value_width + 2))
    print()

    # find padding_multiplier
    if auto_multiplier_detect:
        max_value = max(multiplier_candidate_table)
        for candidate in range(len(multiplier_candidate_table), 0, -1):
            if multiplier_candidate_table[candidate-1] == max_value:
                padding_multiplier = candidate
                break
        print("Padding multiplier is probably: %d" % padding_multiplier)

    # print results:
    # column sum of TRL 6
    old_user_count = math.ceil(trl_sums[6-1] / padding_multiplier)
    # maximum row sum
    new_user_count = math.ceil(max_row_sum / padding_multiplier)
    print("Pre-V1.5 user count:  %d" % old_user_count)
    print("Post-V1.5 user count: %d" % new_user_count)
