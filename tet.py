import re


s = "Asorti31:1 32:2 33:2 34:2 35:2 8'li Koli"
ds = re.sub(r'\d\d:|Asorti:|\d\d.|Asorti :|=\d\W\w+\s\w+|=\d\W\w+|Asorti|\d\w+|\d\D\w+\s\w+', '', s)
print(ds)