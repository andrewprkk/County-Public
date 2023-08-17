import pickle
from pathlib import Path

import streamlit_authenticator as stauth

password = ["FLVCore"] #Replace with the actual password string

hashed_password = stauth.Hasher(password).generate()
print(hashed_password)
print("Hashed password generated and saved successfully.")

