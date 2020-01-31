from mitmproxy import proxy, options
from mitmproxy.tools.dump import DumpMaster
from mitmproxy import flowfilter
from trafficmonitor.database import MitmProxyDb
import datetime


class TrafficMonitor:

    def __init__(self, db_path, ip_address):
        self.host = ip_address
        self.database = MitmProxyDb(db_path, False)
        self.database.conn.isolation_level = None

        self.one_time_creation = True

        # self.req_headers = list()
        # self.res_headers = list()
        self.request_header = ''
        self.response_header = ''
        self.req_data = list()
        self.res_data = list()

    def done(self):
        if self.database.conn is not None:
            self.database.conn.close()

    def request(self, flow):

        ip_filter = "~u %s" % self.host

        if flowfilter.match(ip_filter, flow):

            for req_head in flow.request.headers:
                self.request_header = f"{self.request_header}{req_head} : {flow.request.headers[req_head]}\n"
                # self.req_headers.append(req_head + ":" + flow.request.headers[req_head])

            self.req_data = [
                flow.id,
                str(datetime.datetime.now()),
                str(flow.request.host),
                str(f"{flow.request.url}||{flow.request.http_version}"),
                str(flow.request.method),
                # str(self.req_headers),
                str(self.request_header),  # new header logic
                str(flow.request.text),
                ]

            self.database.conn.execute('INSERT INTO request VALUES (?,?,?,?,?,?,?)', self.req_data)

            del self.req_data[:]
            self.request_header = ''
            # del self.req_headers[:]

    def response(self, flow):

        ip_filter = "~u %s" % self.host

        if flowfilter.match(ip_filter, flow):

            for res_head in flow.response.headers:
                self.response_header = f"{self.response_header}{res_head} : {flow.response.headers[res_head]}\n"

            self.res_data = [
                flow.id,
                str(flow.response.status_code),
                # str(self.res_headers),
                str(self.response_header),  # new header logic
                str(flow.response.text),

            ]

            self.database.conn.execute('INSERT INTO response VALUES (?,?,?,?)', self.res_data)
            del self.res_data[:]
            # del self.res_headers[:]
            self.response_header = ''


def start(**kwargs):
    db_path = kwargs['DBPath']
    ip_address = kwargs['IPAddress']

    opts = options.Options(listen_host='127.0.0.1', listen_port=8080, ssl_insecure=True)

    if 'UpstreamProxyAddress' in kwargs.keys() and 'UpstreamProxyPort' in kwargs.keys():
        opts = options.Options(
            listen_host=kwargs['UpstreamProxyAddress'],
            listen_port=int(kwargs['UpstreamProxyPort']),
            ssl_insecure=True
        )

        # upstream = "upstream:%s:%s" % (kwargs['UpstreamProxyAddress'], kwargs['UpstreamProxyPort'])
        # opts = options.Options(listen_host='127.0.0.1', listen_port=8080, ssl_insecure=True, mode=upstream)

    myaddon = TrafficMonitor(db_path, ip_address)
    pconf = proxy.config.ProxyConfig(opts)
    m = DumpMaster(opts)
    m.server = proxy.server.ProxyServer(pconf)
    m.addons.add(myaddon)
    m.run()
