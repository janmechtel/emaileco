import marimo

__generated_with = "0.7.5"
app = marimo.App(width="full")


@app.cell
def __():
    import marimo as mo
    return mo,


@app.cell
def __(mo):
    mo.md(r"Setup a [Gmail app password](https://support.google.com/accounts/answer/185833?sjid=10666141560394438051-EU)")
    return


@app.cell
def __(mo):
    email_address = mo.ui.text(value="jmechtel@gmail.com", label="email")
    password = mo.ui.text(
        value="XXX", label="password", kind="password"
    )
    mo.vstack([email_address, password])
    return email_address, password


@app.cell
def __(email_address, password, pd):
    import imaplib
    import email

    # Gmail IMAP server and port
    imap_server = "imap.gmail.com"
    imap_port = 993

    # Connect to the IMAP server
    imap = imaplib.IMAP4_SSL(imap_server, imap_port)


    def getEmailsFromServer():
        # Login to your Gmail account
        imap.login(email_address.value, password.value)

        # Select the inbox
        imap.select("INBOX")

        resp, data = imap.uid(
            "FETCH",
            "1:*",
            "(BODY.PEEK[HEADER.FIELDS (Date From To Subject)] RFC822.SIZE X-GM-MSGID)",
        )

        x = 0
        messages = []
        for d in data:
            if len(d) == 2:
                _msg = {}
                line1 = d[0].decode().replace("(X-GM-MSGID", "X-GM-MSGID")
                # print(line1)
                splits1 = line1.split(" ")
                for z in range(1, len(splits1) - 1, 2):
                    if splits1[z] == "X-GM-MSGID":
                        _msg["X-GM-MSGID"] = splits1[z + 1]
                    elif splits1[z] == "RFC822.SIZE":
                        _msg["Size"] = int(splits1[z + 1])
                # print(splits1)
                line2 = d[1].decode()
                # print(line2)
                splits2 = line2.split("\r\n")
                for s in splits2:
                    if s.startswith("To"):
                        _msg["To"] = s.replace("To: ", "")
                    elif s.startswith("From"):
                        _msg["From"] = s.replace("From: ", "")
                    elif s.startswith("Subject"):
                        _msg["Subject"] = s.replace("Subject: ", "")
                    elif s.startswith("Date"):
                        _msg["Date"] = s.replace("Date: ", "")
                messages.append(_msg)

        # Logout from the IMAP server
        print(messages[0])
        print(len(messages))
        imap.logout()
        df = pd.DataFrame(messages)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce", utc=True)
        return df
    return email, getEmailsFromServer, imap, imap_port, imap_server, imaplib


@app.cell
def __(getEmailsFromServer):
    rawGemailDF = getEmailsFromServer()
    return rawGemailDF,


@app.cell
def __():
    import pandas as pd
    return pd,


@app.cell
def __(mo):
    mo.md(r"Find broken To addresse?")
    return


@app.cell
def __(rawGemailDF):
    x = 0
    for _, row in rawGemailDF.iterrows():
        if not isinstance(row["To"], (str, bytes)):
            # print(row)
            x += 1
    print(x)
    return row, x


@app.cell
def __():
    import re


    def extract_email(to_field):
        if not isinstance(to_field, (str, bytes)):
            # print(to_field)
            return to_field
        match = re.search(r"[\w\.-]+@[\w\.-]+", to_field)
        return match.group(0) if match else to_field
    return extract_email, re


@app.cell
def __(extract_email, pd, rawGemailDF):
    import os


    def emailsDF():
        if os.path.exists("emails.csv"):
            _df = pd.read_csv("emails.csv")
        else:
            _df = rawGemailDF.copy()
            _df["To"] = _df["To"].apply(extract_email)
            _df["From"] = _df["From"].apply(extract_email)
            _df["Size"] = _df["Size"].apply(lambda x: round(x / 1024 / 1024,4))
            _df.to_csv("emails.csv", index=False)

        return _df
    return emailsDF, os


@app.cell
def __(emailsDF, mo):
    df = emailsDF()
    df = df.dropna()
    mo.ui.dataframe(df, page_size=400)
    return df,


@app.cell
def __(df, mo):
    df_next = df.copy()
    df_next = df_next[["To", "From", "Size"]]
    df_next = df_next.groupby(["To","From"]).sum()
    df_next.sort_values(by="Size", ascending=False)
    mo.ui.dataframe(df_next, page_size=400)
    return df_next,


@app.cell
def __():
    return


@app.cell
def __():
    return


if __name__ == "__main__":
    app.run()
