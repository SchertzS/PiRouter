from flask import Flask,request
import subprocess

app = Flask(__name__)

wifi_device = "wlan1"

@app.route('/')
def index():

    # Gets list of SSIDs with NetworkManage CLI commands and stores in *result variable.
    result = subprocess.check_output(["nmcli", "--colors", "no", "-m", "multiline", "--get-value", "SSID", "dev", "wifi", "list", "ifname", wifi_device])
    # Decodes the byte string to a normal string and splits it into a list of SSIDs.
    ssids_list = result.decode().split('\n')
    # Builds the HTML dropdown menu with the SSIDs.
    dropdowndisplay = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Wifi Control</title>
        </head>
        <body>
            <h1>Wifi Control</h1>
            <form action="/submit" method="post">
                <label for="ssid">Choose a WiFi network:</label>
                <select name="ssid" id="ssid">
        """
    for ssid in ssids_list:
        only_ssid = ssid.removeprefix("SSID:")
        if len(only_ssid) > 0:
            dropdowndisplay += f"""
                    <option value="{only_ssid}">{only_ssid}</option>
            """
    dropdowndisplay += f"""
                </select>
                <p/>
                <label for="password">Password: <input type="password" name="password"/></label>
                <p/>
                <input type="submit" value="Connect">
            </form>
        </body>
        </html>
        """
    return dropdowndisplay


print("======== \n DEBUG INFO \n========")


@app.route('/submit',methods=['POST'])
def submit():
    # Handles form submission
    if request.method == 'POST':
        # debugging print statement
        print("======== \n DEBUG INFO \n========")
        # prints all form keys submitted
        print(*list(request.form.keys()), sep = ", ")
        # ssid and password values from form
        ssid = request.form['ssid']
        password = request.form['password']
        # connect to wifi network using nmcli command
        connection_command = ["nmcli", "--colors", "no", "device", "wifi", "connect", ssid, "ifname", wifi_device]
        # only add password if one was provided
        if len(password) > 0:
          connection_command.append("password")
          connection_command.append(password)
        result = subprocess.run(connection_command, capture_output=True)
        # return result of connection attempt
        if result.stderr:
            return "Error: failed to connect to wifi network: <i>%s</i>" % result.stderr.decode()
        elif result.stdout:
            return "Success: <i>%s</i>" % result.stdout.decode()
        return "Error: failed to connect."


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)