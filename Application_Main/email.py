import datetime
import sys
import re
import os
from email_validator import validate_email, EmailNotValidError
from pyisemail import is_email

email = sys.argv[1]

# email_pattern = re.compile("^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", re.IGNORECASE)
pattern = r'^[\w\.-]+@[a-zA-Z\d-]+\.[a-zA-Z]{2,}$'
res=is_email(email)

# res = validate_email(email,check_deliverability=True)
print(res)

# if re.match(pattern, email):
#         print("OK")
# else:
#         print("BAD")
