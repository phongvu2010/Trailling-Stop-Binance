from datetime import datetime

str_time = 123400000

a = datetime.fromtimestamp(str_time / 1000)

print(a)