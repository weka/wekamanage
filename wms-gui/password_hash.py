
import yaml
import streamlit_authenticator as stauth

with open("passwd.yaml", "r") as f:
    passwd = yaml.safe_load(f)
    hashed_passwds = stauth.Hasher(
                [passwd['credentials']['usernames']['admin']['password'],
                passwd['credentials']['usernames']['service']['password']]).generate()

    passwd['credentials']['usernames']['admin']['password'] = hashed_passwds[0]
    passwd['credentials']['usernames']['service']['password'] = hashed_passwds[1]

with open("passwd.yaml", "w") as f:
    yaml.safe_dump(passwd, f)