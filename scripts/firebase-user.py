# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/


import firebase_admin
from firebase_admin import credentials, auth

#cred = credentials.Certificate("firebasesa.json")
#firebase_admin.initialize_app(cred)
firebase_admin.initialize_app()
uid = "OFrn1tkdj9MI9GbHt0NkQDpipUq1"
# user = auth.get_user(uid)
auth.set_custom_user_claims(
    uid,
    {
        'subscription_id': 1,
        'active_subscription': 1,
        'subscriptions': [1, 2]
    }
)
uid_2 = "Gn9VoK6O77dSsulWwblOQ6t8WO53"
auth.set_custom_user_claims(
    uid_2,
    {
        'subscription_id': 1,
        'active_subscription': 0,
        'subscriptions': [0, 1]
    }
)

uid_3 = "mcjG10kqGlgz7LyKqUqEMeYgOar1"
auth.set_custom_user_claims(
    uid_3,
    {
        'subscription_id': 1,
        'active_subscription': 0,
        'subscriptions': [0, 1, 2]
    }
)
uid_4 = "Jh0IwHI3RicsriHHVdvdhMwTgLC2"
auth.set_custom_user_claims(
    uid_4,
    {
        'subscription_id': 0,
        'active_subscription': 0,
        'subscriptions': [0, 1, 2]
    }
)

uid_5 = "oMZl4SVEeTURJYsnX8jCuoBfdkt1" # urmet wallbox
auth.set_custom_user_claims(
    uid_5,
    {
        'subscription_id': 1,
        'active_subscription': 1,
        'subscriptions': [1]
    }
)

import requests

__FIREBASE_USER_VERIFY_SERVICE = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword"
# __FIREBASE_API_KEY = "AIzaSyC2yQn0Fdm_Qh9Jm1dxjCpClTHyBEEKtlQ"
__FIREBASE_API_KEY = "AIzaSyDE8tw6q78MgUQABoDLwK5JXPuvImDneHE"
def user_login(email, passwd):
    url = "%s?key=%s" % (__FIREBASE_USER_VERIFY_SERVICE, __FIREBASE_API_KEY)
    data = {"email": email,
            "password": passwd,
            "returnSecureToken": True}
    result = requests.post(url, json=data)
    is_login_successful = result.ok
    json_result = result.json()
    return json_result 