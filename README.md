This is a project for Hackaburg 2026 https://hackaburg.de/2026

The application has multiple data sources, with more easily extensible:
- request `sniffing`
- `dns`
- browser `extension` webrequest URL logging
This can be configured in `bobrnet.config.toml` by simply changing the string.

Start the app:
- clone the repository to any device with python
- `pip install -r requirements.txt` to install the requirements
- `sudo env "PATH=$PATH VIRTUAL_ENV=$VIRTUAL_ENV" python main.py` to start the server with required packages as superuser (so that the DNS server and/or packet sniffer work)

If using Firefox (similar in other servers):
- turn off *"DNS over HTTPS"* and *"Enable DNS over HTTPS using"*. This is due to the fact that some browsers have security measures against packet sniffing, which would prevent the application even detecting most requests.
- open http://localhost:8081/

To (temporarily) install the Firefox extension:
- Switch source in config to "extension"
- Go to `about:debugging` > `This Firefox` > `Load Temporary Add-on...` > select `browser_extension/manifest.json`.
- Clicking the extension in your menu opens the web UI
