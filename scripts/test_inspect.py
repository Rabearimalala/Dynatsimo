# -*- coding: utf-8 -*-
import sys

# Test reading files
with open("src/main.jsx", "rb") as f:
    main_code = f.read()

with open("scripts/api-server.py", "rb") as f:
    api_code = f.read()

print("src/main.jsx bytes:", len(main_code))
print("scripts/api-server.py bytes:", len(api_code))
