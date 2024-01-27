from datetime import datetime

import pytz as pytz

print(datetime.now())
print(datetime.now(pytz.timezone("Europe/Moscow")))
