import yagmail


try:
    receiver = "sayar70931@wowcg.com"
    body = "Hello there from Yagmail"

    yag = yagmail.SMTP("MycalTFG@gmail.com", "MyCalTFG21/22")
    yag.send(
        to=receiver,
        subject="Yagmail test with attachment",
        contents=body, 
    )

    print("Email enviado a " + receiver)
except Exception as ex:
    print("Error: " + str(ex))
