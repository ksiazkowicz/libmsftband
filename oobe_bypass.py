from examples import ExampleClient
from libband.screens import BandScreens

app = ExampleClient()
app.select_device('00:00:00:00:00:00')
oobe_completed = app.device.check_if_oobe_completed()
if not oobe_completed:
    print('Device in OOBE phase')
    # just bypass OOBE
    app.device.navigate_to_screen(BandScreens.OobePressButtonToStart)
else:
    print('Device not in OOBE phase')
app.device.disconnect()
