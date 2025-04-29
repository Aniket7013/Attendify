import http.server
import ssl
import os
import urllib.parse
import subprocess
import re
import datetime
import geopy.distance
import json
import socketserver
import html
import logging

# Constants and Configuration Parameters
PORT = 8001
DIRECTORY = 'E:\\SITE\\PROJECT\\Mega Project\\location_based_attander'
DATA_FILE = os.path.join(DIRECTORY, 'attendance.txt')
KEY_FILE = os.path.join(DIRECTORY, '192.168.174.172-key.pem')
CERT_FILE = os.path.join(DIRECTORY, '192.168.174.172.pem')

ACCEPTED_DATE = datetime.date(2024, 11, 30)  # Date when attendance can be marked
START_TIME = datetime.time(9, 0)  # Start time for attendance marking
END_TIME = datetime.time(23, 0)  # End time for attendance marking

ACCEPTED_LOCATION = (28.957686733024183, 77.63297831372378)  # Latitude and longitude of the center point
ACCEPTED_RADIUS = 10.0  # Radius in kilometers

# Error messages
ERROR_MSG_INVALID_DATE_TIME = b'Attendance can only be marked from 9:00 AM to 11:00 PM.'
ERROR_MSG_OUT_OF_LOCATION = b'You are not within the allowed location to mark attendance.'
ERROR_MSG_ALREADY_MARKED = b'Attendance already marked.'
ERROR_MSG_EMPTY_POST_DATA = b'Error parsing JSON or empty POST data'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path == '/':
                self.path = '/index.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        except Exception as e:
            logging.error(f"Error handling GET request: {e}")
            self.send_response(500)
            self.end_headers()

    def do_POST(self):
        if self.path == '/check-location':
            self.handle_check_location()
        else:
            self.handle_mark_attendance()

    def handle_check_location(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            if not post_data:
                raise ValueError("Empty POST data received")

            parsed_data = json.loads(post_data.decode('utf-8'))

            latitude = float(parsed_data.get('latitude', 0.0))
            longitude = float(parsed_data.get('longitude', 0.0))

            if self.is_within_location(latitude, longitude):
                self.respond_with_json({'status': 'valid'})
            else:
                self.respond_with_json({'status': 'invalid'})
        except ValueError as ve:
            logging.error(f"Error parsing JSON or empty POST data: {ve}")
            self.send_response(400)
            self.end_headers()
            self.wfile.write(ERROR_MSG_EMPTY_POST_DATA)
        except Exception as e:
            logging.error(f"Error handling check-location: {e}")
            self.send_response(500)
            self.end_headers()

    def handle_mark_attendance(self):
        try:
            if not self.is_within_time_range():
                self.send_response(403)
                self.end_headers()
                self.wfile.write(ERROR_MSG_INVALID_DATE_TIME)
                return

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            parsed_data = urllib.parse.parse_qs(post_data.decode('utf-8'))

            name = html.escape(parsed_data.get('name', [''])[0])
            gp_id = html.escape(parsed_data.get('password', [''])[0])
            latitude = float(parsed_data.get('latitude', ['0.0'])[0])
            longitude = float(parsed_data.get('longitude', ['0.0'])[0])
            client_ip = self.client_address[0]
            mac_address = self.get_mac_address(client_ip)

            logging.info(f"Received POST request: name={name}, gp_id={gp_id}, client_ip={client_ip}, mac_address={mac_address}")

            if not self.is_within_location(latitude, longitude):
                self.send_response(403)
                self.end_headers()
                self.wfile.write(ERROR_MSG_OUT_OF_LOCATION)
                return

            if self.is_present_already_marked(gp_id, client_ip, mac_address):
                self.send_response(403)
                self.end_headers()
                self.wfile.write(ERROR_MSG_ALREADY_MARKED)
                logging.info(f"Attendance already marked for GP ID={gp_id}, IP: {client_ip}, MAC: {mac_address}")
            else:
                self.mark_attendance(name, gp_id, client_ip, mac_address)
                self.send_response(301)
                self.send_header('Location', '/second-page.html')
                self.end_headers()
                logging.info(f"Marked attendance for {name} with GP ID: {gp_id}, IP: {client_ip} and MAC: {mac_address}")
        except Exception as e:
            logging.error(f"Error handling POST request: {e}")
            self.send_response(500)
            self.end_headers()

    def is_within_time_range(self):
        current_datetime = datetime.datetime.now()
        return (current_datetime.date() == ACCEPTED_DATE and
                START_TIME <= current_datetime.time() <= END_TIME)

    def is_within_location(self, latitude, longitude):
        try:
            if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
                logging.error(f"Invalid latitude or longitude values: {latitude}, {longitude}")
                return False

            student_location = (latitude, longitude)
            distance = geopy.distance.distance(ACCEPTED_LOCATION, student_location).km

            logging.info(f"Distance from accepted location: {distance} km")

            return distance <= ACCEPTED_RADIUS
        except Exception as e:
            logging.error(f"Error checking location: {e}")
            return False

    def is_present_already_marked(self, gp_id, ip, mac):
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        entry = line.strip().split(',')
                        if gp_id == entry[1] or ip == entry[2] or mac == entry[3]:
                            logging.info(f"Found existing entry with GP ID, IP, or MAC: {line.strip()}")
                            return True
        except Exception as e:
            logging.error(f"Error checking attendance: {e}")
        return False

    def mark_attendance(self, name, gp_id, ip, mac):
        try:
            with open(DATA_FILE, 'a') as f:
                entry = f'{name},{gp_id},{ip},{mac}\n'
                f.write(entry)
                logging.info(f"Attendance recorded: {entry.strip()}")
        except Exception as e:
            logging.error(f"Error marking attendance: {e}")

    def get_mac_address(self, ip):
        try:
            pid = subprocess.Popen(["arp", "-a"], stdout=subprocess.PIPE)
            s = pid.communicate()[0].decode('utf-8')
            lines = s.split('\n')
            for line in lines:
                if ip in line:
                    mac = re.search(r'([a-fA-F0-9]{2}[:|\-]?){6}', line).group(0)
                    return mac
        except Exception as e:
            logging.error(f"Error getting MAC address: {e}")
        return '00:00:00:00:00:00'

    def sanitize_path(self, path):
        sanitized_path = os.path.normpath(os.path.join(DIRECTORY, path.lstrip('/')))
        if os.path.commonprefix([sanitized_path, DIRECTORY]) != DIRECTORY:
            return DIRECTORY  # Default to DIRECTORY if traversal outside is attempted
        return sanitized_path

    def translate_path(self, path):
        try:
            sanitized_path = self.sanitize_path(path)
            return sanitized_path
        except Exception as e:
            logging.error(f"Error translating path: {e}")
            return os.path.join(DIRECTORY, 'index.html')

    def respond_with_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """Handle requests in a separate thread."""
    pass


Handler = MyHttpRequestHandler

server_address = ('0.0.0.0', PORT)
httpd = ThreadedHTTPServer(server_address, Handler)

httpd.socket = ssl.wrap_socket(httpd.socket,
                               keyfile=KEY_FILE,
                               certfile=CERT_FILE,
                               server_side=True)

logging.info(f"Serving on https://0.0.0.0:{PORT}")
httpd.serve_forever()
