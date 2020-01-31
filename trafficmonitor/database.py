from pathlib import Path
import sqlite3
import logging

from trafficmonitor.helper_functions import create_path

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

log_path = str(Path(f"{create_path()}/database.log"))
file_handler = logging.FileHandler(log_path)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class MitmProxyDb:
    def __init__(self, path, check_same_thread=True):
        try:

            self.conn = sqlite3.connect(path, check_same_thread=check_same_thread)
            self.cursor = self.conn.cursor()

        except sqlite3.Error:

            logger.exception('Unable to initialize the database')

        self.create_table()

    def create_table(self):
        try:

            self.cursor.execute(
                 'CREATE TABLE IF NOT EXISTS request (ID TEXT, DATETIME TEXT, HOST TEXT, URL TEXT, METHOD TEXT, '
                 'HEADERS TEXT, CONTENT TEXT); '
            )

            self.cursor.execute(
                'CREATE TABLE IF NOT EXISTS response (ID TEXT, STATUS_CODE TEXT, HEADERS TEXT, CONTENT TEXT);'
            )

        except sqlite3.Error:
            logger.exception("Unable to Create Table")

    def request_data(self, data):
        try:

            self.cursor.execute('INSERT INTO request VALUES (?,?,?,?,?,?,?)', data)
            self.conn.commit()

        except sqlite3.Error:
            logger.exception("Unable to add values to request table")

    def response_data(self, data):
        try:

            self.cursor.execute('INSERT INTO response VALUES (?,?,?,?)', data)
            self.conn.commit()

        except sqlite3.Error:
            logger.exception("Unable to add values to response table")

    def refresh_data(self, **kwargs):
        try:

            if "_from" in kwargs.keys() and "_to" in kwargs.keys():

                _from = str(kwargs['_from'])
                _to = str(kwargs['_to'])

                self.cursor.execute('SELECT request.ID, request.DATETIME, request.HOST, request.URL, '
                                    'response.STATUS_CODE, request.METHOD FROM request LEFT JOIN response ON '
                                    'request.ID = response.ID WHERE DATETIME BETWEEN ? AND ?''',
                                    (_from, _to))
                rows = self.cursor.fetchall()
                return rows

            elif "_to" in kwargs.keys():
                _to = str(kwargs['_to'])

                self.cursor.execute('SELECT request.ID, request.DATETIME, request.HOST, request.URL, '
                                    'response.STATUS_CODE, request.METHOD FROM request LEFT JOIN response ON '
                                    'request.ID = response.ID WHERE DATETIME < ?''', (_to,))
                rows = self.cursor.fetchall()
                return rows

            elif "_from" in kwargs.keys():
                _from = str(kwargs['_from'])

                self.cursor.execute('SELECT request.ID, request.DATETIME, request.HOST, request.URL, '
                                    'response.STATUS_CODE, request.METHOD FROM request LEFT JOIN response ON '
                                    'request.ID = response.ID WHERE DATETIME > ?''', (_from,))
                rows = self.cursor.fetchall()
                return rows

            else:
                self.cursor.execute('''
                                    SELECT request.ID, request.DATETIME, request.HOST, request.URL,
                                    response.STATUS_CODE, request.METHOD
                                    FROM request LEFT JOIN response ON request.ID = response.ID
                                    ''')
                rows = self.cursor.fetchall()
                return rows

        except sqlite3.Error:
            logger.exception("Unable to refresh data")

    def display_request_data(self, proxy_id):
        try:

            self.cursor.execute('''
                SELECT HEADERS, CONTENT, URL FROM request WHERE ID = \'%s\'''' % proxy_id)
            rows = self.cursor.fetchall()
            return rows

        except sqlite3.Error:
            logger.exception("Unable to display request data")

    def display_response_data(self, proxy_id):
        try:

            self.cursor.execute('''
                SELECT HEADERS, CONTENT FROM response WHERE ID = \'%s\'''' % proxy_id)
            rows = self.cursor.fetchall()
            return rows

        except sqlite3.Error:
            logger.exception("Unable to display response data")

    def export_sessions(self, proxy_id):
        try:
            self.cursor.execute('''SELECT request.URL, request.HEADERS, request.CONTENT, request.METHOD, 
            response.STATUS_CODE, response.HEADERS FROM request LEFT JOIN response ON request.ID = response.ID WHERE 
            request.ID = \'%s\'''' % proxy_id)
            rows = self.cursor.fetchall()
            return rows

        except sqlite3.Error:
            logger.exception("Unable to export request data")

    # def export_json_response(self, proxy_id):
    #     try:
    #
    #         self.cursor.execute('''SELECT STATUS_CODE, HEADERS FROM response WHERE ID = \'%s\'''' % proxy_id)
    #         rows = self.cursor.fetchall()
    #         return rows
    #
    #     except sqlite3.Error:
    #         logger.exception("Unable to export response data")

    def export_request(self, proxy_id):
        try:

            self.cursor.execute('''SELECT * FROM request WHERE ID = \'%s\'''' % proxy_id)
            rows = self.cursor.fetchall()
            return rows

        except sqlite3.Error:
            logger.exception("Unable to export request data")

    def export_response(self, proxy_id):
        try:

            self.cursor.execute('''SELECT * FROM response WHERE ID = \'%s\'''' % proxy_id)
            rows = self.cursor.fetchall()
            return rows

        except sqlite3.Error:
            logger.exception("Unable to export response data")

    def run_selected_request(self, proxy_id):
        try:

            self.cursor.execute('SELECT ID, HOST, URL, HEADERS, METHOD, CONTENT FROM request WHERE ID=?', (proxy_id,))
            rows = self.cursor.fetchone()
            return rows

        except sqlite3.Error:
            logger.exception("Unable to run selected result")

    def return_header_audit_data(self):
        try:
            self.cursor.execute('''
            SELECT request.DATETIME, request.HOST, request.URL, request.METHOD, response.STATUS_CODE,
            response.HEADERS FROM request INNER JOIN response ON request.ID = response.ID
            ''')
            rows = self.cursor.fetchall()
            return rows

        except sqlite3.Error:
            logger.exception("Unable to refresh data")

    def close_connection(self):
        try:

            self.conn.close()

        except sqlite3.Error:
            logger.exception("Unable to close sqlite3 connection")

    def export_txt(self, proxy_id):
        try:
            self.cursor.execute('SELECT request.METHOD, request.URL, request.HEADERS, request.CONTENT,'
                                'response.STATUS_CODE, response.HEADERS, response.CONTENT FROM request LEFT JOIN '
                                'response ON request.ID = response.ID WHERE request.ID = ?', (proxy_id,))
            rows = self.cursor.fetchall()
            return rows
        except sqlite3.Error:
            logger.exception("Unable to export session data to text file")