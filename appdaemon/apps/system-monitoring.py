"""Define automations for system monitoring."""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.request import urlopen
from packaging import version

from appbase import AppBase

# class NotifyAppDaemonError(AppBase):
#     """Define a base class for notification on AppDaemon errors."""

#     APP_SCHEMA = APP_SCHEMA.extend({vol.Required("targets"): cv.ensure_list})

#     def configure(self) -> None:
#         """Configure."""
#         # Listen for errors in the appdaemon log files
#         self.targets = self.args["targets"]
#         self.adbase.listen_log(self.on_log_error, log="error_log")

#     def on_log_error(
#         self, name: str, ts: str, level: str, type: str, message: str, kwargs: dict
#     ) -> None:
#         self.adbase.log(f"Send notification about AppDaemon Error to {self.targets}.")
#         """Notify on Error."""
#         self.notification_manager.notify(
#             channel="smart_home",
#             message=f"Es gab einen Fehler in AppDaemon!",
#             title=f"AppDaemon Fehler",
#             targets=self.targets,
#         )


class LatestConBeeFirmware(AppBase):
    """Define a base class for getting the latest ConBee firmeware version."""

    def configure(self) -> None:
        self.url = "http://deconz.dresden-elektronik.de/deconz-firmware/"
        self.adbase.run_every(self.update_latest_version_sensor, "now", 60 * 60)

    def update_latest_version_sensor(self, *args) -> None:
        urls = self.get_url_paths(self.url)
        urls_filtered = [url for url in urls if "ConBeeII" in url]
        urls_with_dates = {url: self.get_last_modified_date(url) for url in urls_filtered}
        latest_url = max(urls_with_dates, key=urls_with_dates.get)
        version = latest_url.split("ConBeeII_")[1].strip(".bin.GCF")

        self.hass.set_state(
            "sensor.latest_firmware_conbee",
            state=version,
            attributes={"friendly_name": "Firmware ConBee II"}
        )

    def get_url_paths(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        parent = [url + node.get('href') for node in soup.find_all('a') if node.get('href').endswith("GCF")]
        return parent

    def get_last_modified_date(self, url):
        u = urlopen(url)
        headers = dict(u.getheaders())
        last_modified = headers['Last-Modified']
        return datetime.strptime(last_modified, "%a, %d %b %Y %H:%M:%S %Z")