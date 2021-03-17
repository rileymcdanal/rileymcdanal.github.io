import os
import sys

password = sys.argv[1]
print(os.listdir())
print(type(os.environ['DRIVE_SECRET']))
print(type(os.environ['DRIVE_SECRET'][0]))
print(os.system('gpg --version'))
os.system(f"""gpg --quiet --batch --yes --decrypt --passphrase="{os.environ['DRIVE_SECRET']}" --output token.json token.json.gpg""")
