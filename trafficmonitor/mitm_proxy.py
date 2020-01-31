from pathlib import Path
import multiprocessing

from trafficmonitor.trafficviewer import start
from trafficmonitor.helper_functions import create_path


class MitmProxy:
    """ class for mitmproxy configuration """

    def __init__(self):
        # default command for mitmdump lib
        self.command = ""
        self.proxy_pid = str()

        # Data store path
        self.path = create_path()

        # proxy process initialization
        self.proxy_process = None

    def start_proxy(self, value):
        """method which will start the mitm process separately from main process"""

        proxy_data = {
            "IPAddress": value['IP_ADDRESS'],
            "DBPath": str(Path(f"{self.path}/{value['EXECUTION_NAME']}.db")),

        }

        if 'UPSTREAM_PROXY_IP' in value.keys() and 'UPSTREAM_PROXY_PORT' in value.keys():

            proxy_data['UpstreamProxyAddress'] = value['UPSTREAM_PROXY_IP']
            proxy_data['UpstreamProxyPort'] = value['UPSTREAM_PROXY_PORT']

        self.proxy_process = multiprocessing.Process(target=start, kwargs={**proxy_data})
        self.proxy_process.daemon = True
        self.proxy_process.start()

    def stop_proxy(self):
        """method to stop mitm process"""
        try:
            self.proxy_process.terminate()
        except AttributeError:
            pass
