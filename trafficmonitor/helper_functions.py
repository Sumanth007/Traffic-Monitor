import re
from pathlib import Path
from platform import system
from subprocess import PIPE, call


def get_json(path):
    """"function to convert json file into dictionary"""
    import json
    with open(path, "r") as f:
        return json.load(f)


def get_status_code_value(status_code):
    """function to return appropriate status code value from the dictionary"""
    status_code_dict = {
        "100": "Continue", "101": "Switching Protocols", "200": "OK", "201": "Created",
        "202": "Accepted", "203": "Non-authoritative Information", "204": "No Content",
        "205": "Reset Content", "206": "Partial Content", "300": "Multiple Choices",
        "301": "Moved Permanently", "302": "Found", "303": "See Other", "304": "Not Modified",
        "305": "Use Proxy", "306": "Unused", "307": "Temporary Redirect", "400": "Bad Request",
        "401": "Unauthorized", "402": "Payment Required", "403": "Forbidden", "404": "Not Found",
        "405": "Method Not Allowed", "406": "Not Acceptable", "407": "Proxy Authentication Required",
        "408": "Request Timeout", "409": "Conflict", "410": "Gone", "411": "Length Required",
        "412": "Precondition Failed", "413": "Request Entity Too Large", "414": "Request-url Too Long",
        "415": "Unsupported Media Type", "416": "Requested Range Not Satisfiable",
        "417": "Expectation Failed", "500": "Internal Server Error", "501": "Not Implemented",
        "502": "Bad Gateway", "503": "Service Unavailable", "504": "Gateway Timeout",
        "505": "HTTP Version Not Supported", "No Response": ""
    }

    return status_code_dict[status_code]


def post_parser(data):
    tmp_dict = dict()
    if len(data) > 0:
        split_data = str(data).split("&")
        if len(split_data) > 1:
            for value in split_data:
                if not re.search(r"[cC][sS][rR][fF][tT][oO][kK][eE][nN]", value):
                    tmp = value.split("=", 1)
                    tmp_dict[tmp[0]] = tmp[1]

    return tmp_dict


def put_parser(body_data):
    body_tags = re.findall(
        r"<[a-zA-Z0-9~@#$^*()_+=[\]{}|\\,.?:-]*>"
        r"[a-zA-Z0-9~@#$^*()_+=[\]{}|\\/,.?:-]*"
        r"</[a-zA-Z0-9~@#$^*()_+=[\]{}|\\/,.?:-]*>",
        body_data
    )

    tags = [tags for tags in body_tags if tags[1] != '/' and tags[-1] != '/']

    tmp_dict = {}
    for tag in tags:
        start_tag = re.search(r"<(.*?)>", tag).group(1)
        actual_value = re.search(r">(.*?)</", tag).group(1)

        tmp_dict[start_tag] = actual_value

    return tmp_dict


def ping(ip_address):
    """ ping to the host and check host is alive or dead and send the response """
    param = "-n" if system().lower() == "windows" else "-c"
    command = ['ping', param, '1', ip_address]

    return call(command, stdout=PIPE) == 0


def get_header_dict(value):
    """function to convert string header to dictionary"""
    values = value.rstrip("\n").split("\n")
    header_dict = {}
    for value in values:
        key, value = value.split(":", 1)
        header_dict[key.rstrip().lstrip()] = value.lstrip().rstrip()

    return header_dict


def create_path():
    """function to create traffic monitor directory"""
    data_store_path = '~/Documents/TrafficMonitor'
    path = Path(data_store_path).expanduser()
    path.mkdir(parents=True, exist_ok=True)
    return str(path)

