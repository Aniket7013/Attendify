# Attendify – Location-Based Attendance System

**Attendify** is a secure, location-based attendance marking system designed for educational institutions and organizations. It ensures that attendance is only marked from an authorized geographic location within a specific time window, helping to prevent proxy or remote check-ins.


## 🔐 Features
- 📍 **Location Verification**: Users must be within a set radius to mark attendance.
- ⏰ **Time Restriction**: Attendance can only be marked during defined hours and date.
- ✅ **Duplicate Prevention**: Detects repeated attendance attempts using IP and MAC address.
- 🔒 **Secure Server**: HTTPS-based server with SSL certificates.
- 🧭 **Geolocation API**: Uses browser-based location access to verify user coordinates.
- 🖥️ **Modern UI**: Clean and responsive front-end with interactive elements.


## 📁 Project Structure
```
Attendify/
├── attendance.txt         # (Generated) File storing attendance records
├── index.html             # Main login and location verification page
├── second-page.html       # Confirmation page after attendance is marked
├── script.js              # Handles geolocation and button logic
├── styles.css             # Frontend styling
├── serverpy.py            # Python HTTPS server with attendance logic
├── localhost-key.pem      # SSL key file for local secure connections
└── logosub.png            # Logo image used in the frontend
```


## ⚙️ How It Works
1. **User Login**: Enters name and enrollment ID.
2. **Location Verification**: Must be within the defined latitude-longitude radius.
3. **Server Validation**: Checks if:
   - Request is within date & time range.
   - Location is authorized.
   - Attendance isn't already marked using GP ID/IP/MAC.
4. **Attendance Marked**: On success, logs data to a file and redirects to the confirmation page.


## ✅ Technologies Used
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (`http.server`, `ssl`, `geopy`)
- **Security**: HTTPS with SSL/TLS, MAC & IP tracking


## 🛠️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/Aniket7013/attendify.git
cd attendify
```

### 2. Install dependencies
```bash
pip install geopy
```

### 3. Run the server
```bash
python serverpy.py
```

### 4. Open in browser
Navigate to: `https://localhost:8001`

> ⚠️ You might need to allow security exceptions in your browser due to self-signed SSL.

## 🔐 Important Notes
- No actual credentials are stored.
- You must use **valid `.pem` and `.key` files** for local HTTPS.
- Data is logged in plain text (`attendance.txt`). For production, consider using a database.

## 🙋‍♂️ Developer
Made with ❤️ by [Aniket Rai](https://linktr.ee/aniket.rai)
