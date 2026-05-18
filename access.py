# =========================================================
# access.py
# ZERODHA KITE ACCESS TOKEN GENERATOR
# =========================================================

from kiteconnect import KiteConnect

# =========================================================
# API DETAILS
# =========================================================

API_KEY = "2fny2gd8v1yxolco"

API_SECRET = "pcy4jveq7e9d8g3n1yrv0pi63f5u9n0j"

# =========================================================
# KITE OBJECT
# =========================================================

kite = KiteConnect(
    api_key=API_KEY
)

# =========================================================
# LOGIN URL
# =========================================================

print("\nOPEN THIS URL IN BROWSER:\n")

print(
    kite.login_url()
)

# =========================================================
# REQUEST TOKEN
# =========================================================

request_token = input(
    "\nPASTE REQUEST TOKEN : "
)

# =========================================================
# GENERATE SESSION
# =========================================================

try:

    data = kite.generate_session(
        request_token=request_token,
        api_secret=API_SECRET
    )

    access_token = data[
        "access_token"
    ]

    # =====================================================
    # SAVE ACCESS TOKEN
    # =====================================================

    with open(
        "access_token.txt",
        "w"
    ) as f:

        f.write(access_token)

    print("\nACCESS TOKEN SAVED")

    print(
        "\nACCESS TOKEN:\n"
    )

    print(access_token)

except Exception as e:

    print(
        f"\nERROR : {e}"
    )