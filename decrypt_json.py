import os
import sys

password = sys.argv[1]

os.system(f"""gpg --quiet --batch --yes --decrypt --passphrase="{password}" --output token.json token.json.gpg""")
