import os
import sys

password = sys.argv[1]
print(os.listdir())
print(os.environ['DRIVE_SECRET'] == password)
os.system(f"""gpg --quiet --batch --yes --decrypt --passphrase="{password}" --output token.json token.json.gpg""")
