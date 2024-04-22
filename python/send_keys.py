import win32com.client
import time
shell = win32com.client.Dispatch("WScript.Shell")
time.sleep(1)
shell.AppActivate("Scripture Forge - Google Chrome")
v1 = r"Kədarəŋ kati kȧ Nahomɛŋ ɔninkȧrȧ kɔŋ ɔ kanɛ kɔ kəpa, ‘‘Wan kȧmi bɛra, I gbəliyɛ thɛnsȧ mu məyirȧ, kanka pə yi ɔfinɔ ta ȧtȧmu-i?"
for character in v1:
    shell.SendKeys(character)
    time.sleep(1)