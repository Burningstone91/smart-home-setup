"""Define automations for system monitoring."""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.request import urlopen
from packaging import version

import adbase as ad

class LatestConBeeFirmware(ad.ADBase):
    """Define a base class for getting the latest ConBee firmeware version."""

    def initialize(self) -> None:
        """Initialize."""
        self.adbase = self.get_ad_api()
        self.hass = self.get_plugin_api("HASS")
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