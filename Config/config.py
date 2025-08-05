import tomllib
import sys
if 'linux' == sys.platform:
    with open("./Config/config.toml", "rb") as f:
        data = tomllib.load(f)
else:
    with open("./Config/config.toml", "rb") as f:
        data = tomllib.load(f)


users = data['users']
connection = data['connection']
host = data['host']
header = data['header']['header']
tail = data['header']['tail']
print_reports = data['reports']