import os
import sys

os.system(f"""gpg --quiet --batch --yes --decrypt --passphrase="{os.environ['DRIVE_SECRET']}" --output token.json token.json.gpg""")
