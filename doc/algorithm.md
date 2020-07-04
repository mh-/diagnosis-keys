## TRL Profile

The TRL (transmission risk level) profile determines the TRL that is attached to each Diagnosis Key.
For each day in the past, a value from this list is selected by the cwa-app:
```
trl_profile = [5, 6, 8, 8, 8, 5, 3, 1, 1, 1, 1, 1, 1, 1]  # 0: today, 1: yesterday, ... 
```
Today's key is not uploaded, so the maximum numbers of keys that can be uploaded is 13.
(Case 4 / Fig. 14 in https://github.com/corona-warn-app/cwa-documentation/blob/master/transmission_risk.pdf)

## Counting Users

After https://github.com/corona-warn-app/cwa-app-android/issues/678 
was fixed, and using a Android app that contains the fix is now enforced by cwa-server,
every user will - at the moment - at least submit exactly one key with TRL == 6.
So this could be used to count the number of users submitting keys.
Note that this can change when https://github.com/corona-warn-app/cwa-documentation/issues/343 
will be fixed, because then a user might upload older keys, but not yesterday's key.

## Counting Keys per User

A simple algorithm tracks the TRL profile chain through the list of Diagnosis Keys and stops at 13,
or when it doesn't find the correct TRL in any keys from the previous day. Each found key is counted 
and then deleted from the list.

However there is a problem with _missing keys_: 
The simple algorithm fails if a user has stopped Exposure Notifications for at least one day, 
because then a key was not generated nor uploaded for that day. This would result in non-parsed keys.

Before we improve the algorithm, let's first look at corner cases that could happen.

Assuming the currently uploaded TRL profiles (with #343 not fixed), _missing keys_ would require that
the algorithm searches for a key with the previous day's TRL not only in previous day's keys, but also
in older keys, for up to -13 days. If TRL paths cross, the wrong path might be followed, but that would
still yield correct counts.

With #343 fixed, _missing keys_ could cause scenarios like these:

```
        01 02 03 04 05 06 07 08 09 10 11 12 13
user a      8  8  8  5  3                       # 5 keys
user b                     1  1  1  1  1  1  1  # 7 keys
user c   6                                      # 1 key

mixed    6  8  8  8  5  3  1  1  1  1  1  1  1  # 1 user with 13 keys
```
```
        01 02 03 04 05 06 07 08 09 10 11 12 13
user a   6  8  8  8  5  3  1                    # 7 keys
user b                     1  1  1  1  1  1  1  # 7 keys

mixed    6  8  8  8  5  3  1  1  1  1  1  1  1  # 1 user with 13 keys
                           1                    # 1 user with 1 key
```
So with #343 fixed, the result of the (desired) anonymization on the server would be that 
the number of users counted by the algorithm will likely be **lower than in reality** 
and the keys per user cannot be counted correctly anymore.
