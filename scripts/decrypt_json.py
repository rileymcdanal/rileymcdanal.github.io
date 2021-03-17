import os
import sys

password = sys.argv[1]
print(os.listdir())
print(password[0])
os.system(f"""gpg --quiet --batch --yes --decrypt --passphrase="{os.environ['DRIVE_SECRET']}" --output token.json token.json.gpg""")
