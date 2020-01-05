# Lucy-Bot
A Discord bot that proxies messages through Kik.

## How to use

To use this, you must have a Kik account and a Discord Bot (and its authentication Token). Additionally, you should have that bot invited to a single discord server which will be used to both view kik messages and send them.

In `secret.py`, add your Discord bot's token, your Kik username and password. Also add a unique [device id (16 random bytes)](https://www.random.org/cgi-bin/randbyte?nbytes=16&format=h) and [android id (8 random bytes)](https://www.random.org/cgi-bin/randbyte?nbytes=8&format=h) to that file, and if you have an apk from a recent version of Kik, feel free to set a [custom kik version](https://github.com/tomer8007/kik-bot-api-unofficial/blob/new/kik_unofficial/device_configuration.py#L9) (which may keep you from solving a captcha each time the script is restarted).

Once this is done, run either `python3 lucy.py` or `./startlucy.sh`. For me, the second one (which restarts the bot every hour) was required (possibly either because of bad internet or Kik closing my connection to their server).
