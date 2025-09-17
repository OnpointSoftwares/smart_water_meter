# Smart Water Meter System

A comprehensive IoT-based water monitoring system built with Arduino (NodeMCU ESP8266), Django (Python), and Bootstrap frontend.

## 🌟 Features

### IoT Device (Arduino)
- **Real-time Monitoring**: Water flow measurement using YF-S201 sensor
- **WiFi Connectivity**: Automatic data transmission every 10 seconds
- **Local Caching**: Offline data storage when WiFi is unavailable
- **LED Indicators**: Visual status feedback for device and connectivity
- **Automatic Retry**: Robust error handling and retry mechanisms

### Backend (Django)
- **REST API**: Complete API for data collection and retrieval
- **Device Management**: Multi-device support with API key authentication
- **User Authentication**: JWT tokens for web users, API keys for devices
- **Alert System**: Automatic leak detection and excessive usage alerts
- **Admin Panel**: Comprehensive device and user management

### Frontend (Bootstrap)
- **Responsive Dashboard**: Real-time consumption monitoring
- **Interactive Charts**: Chart.js visualizations for usage trends
- **Device Status**: Live device monitoring and status indicators
- **Alert Management**: Real-time alert notifications
- **Billing System**: Consumption-based cost calculations

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Arduino IDE
- NodeMCU ESP8266
- YF-S201 Water Flow Sensor

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smartwatermeter
   ```

2. **Set up Python environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Set up database**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python setup_admin.py  # Creates admin user
   ```

5. **Run the server**
   ```bash
   python manage.py runserver
   ```

6. **Access the system**
   - Web Interface: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin
   - API Documentation: http://localhost:8000/api/

## 🔧 Hardware Setup

### Components Required
- NodeMCU ESP8266 development board
- YF-S201 Water Flow Sensor
- Jumper wires
- Breadboard (optional)

### Wiring Diagram
```
YF-S201 Water Flow Sensor -> NodeMCU ESP8266
================================
Red wire (VCC)    -> 3.3V or 5V
Black wire (GND)  -> GND
Yellow wire (Data) -> D2 (GPIO4)
```

### Arduino Setup
1. Install ESP8266 board package in Arduino IDE
2. Install required libraries:
   - ArduinoJson
   - NTPClient
3. Configure WiFi credentials and server URL in the Arduino code
4. Upload the code to NodeMCU

## 📱 Usage

### Web Dashboard
1. Login with your credentials
2. View real-time water consumption
3. Monitor device status
4. Check alerts and notifications
5. Review billing and usage reports

### Device Management
1. Access admin panel at `/admin`
2. Add new devices with unique IDs
3. Generate API keys for device authentication
4. Monitor device connectivity and status

### API Endpoints

#### Device Data Submission
```http
POST /api/data/
Content-Type: application/json
X-API-Key: your-device-api-key

{
    "device_id": "DEVICE_001",
    "flow_rate": 2.5,
    "total_consumption": 1250.0,
    "pulse_count": 562500,
    "timestamp": 1640995200
}
```

#### Get Usage Data
```http
GET /api/data/list/?device_id=DEVICE_001&start_date=2024-01-01
Authorization: Bearer your-jwt-token
```

#### Dashboard Statistics
```http
GET /api/dashboard/stats/
Authorization: Bearer your-jwt-token
```

## ⚙️ Configuration

### Environment Variables
```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
WATER_RATE_PER_LITER=0.002
LEAK_THRESHOLD_LITERS_PER_HOUR=50
EXCESSIVE_USAGE_THRESHOLD_LITERS_PER_DAY=500
```

### Arduino Configuration
```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverURL = "http://your-server.com/api/data/";
const char* deviceID = "DEVICE_001";
const char* apiKey = "your-device-api-key";
```

## 🔔 Alert System

### Leak Detection
- Monitors continuous flow for extended periods
- Configurable threshold (default: 50L/hour)
- Automatic alert generation

### Excessive Usage
- Daily consumption monitoring
- Configurable threshold (default: 500L/day)
- Email/SMS notifications

### Device Offline
- Monitors device connectivity
- Alerts when devices go offline
- Automatic recovery detection

## 💰 Billing System

### Features
- Consumption-based billing
- Monthly/weekly billing cycles
- Automatic cost calculations
- PDF bill generation
- Payment tracking

### Rate Configuration
- Configurable rate per liter
- Tiered pricing support
- Tax calculations
- Discount management

## 🔒 Security

### Authentication
- JWT tokens for web users
- API keys for IoT devices
- Role-based access control
- Session management

### Data Protection
- HTTPS support
- API rate limiting
- Input validation
- SQL injection protection

## 📊 Monitoring & Analytics

### Real-time Dashboard
- Live consumption data
- Device status monitoring
- Alert notifications
- Usage trends

### Reports
- Daily/weekly/monthly reports
- Consumption analytics
- Cost analysis
- Export capabilities

## 🛠️ Development

### Project Structure
```
smartwatermeter/
├── arduino_code/          # Arduino/NodeMCU code
├── smart_water_meter/      # Django project settings
├── water_meter/           # Main Django app
├── templates/             # HTML templates
├── static/               # CSS, JS, images
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

### API Documentation
The system provides a complete REST API for:
- Device data submission
- Usage data retrieval
- Device management
- User authentication
- Alert management

### Database Models
- **Device**: Water meter device information
- **WaterUsage**: Consumption readings
- **Alert**: System alerts and notifications
- **UserProfile**: Extended user information
- **Bill**: Billing and payment records

## 🚨 Troubleshooting

### Common Issues

1. **Device Not Connecting**
   - Check WiFi credentials
   - Verify server URL accessibility
   - Check API key validity

2. **No Data Received**
   - Verify sensor wiring
   - Check device power supply
   - Monitor serial output for errors

3. **Alerts Not Working**
   - Check threshold configurations
   - Verify email settings
   - Check alert rules

### Debug Mode
Enable debug mode in `.env`:
```env
DEBUG=True
```

### Logs
Monitor Django logs for detailed error information:
```bash
python manage.py runserver --verbosity=2
```

## 📈 Scaling

### Multiple Devices
- Support for unlimited devices per user
- Device grouping and management
- Bulk operations

### Performance
- Database indexing for large datasets
- Caching for frequently accessed data
- API pagination

### Deployment
- Docker support
- Cloud deployment guides
- Load balancing configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the API documentation

## 🔮 Future Enhancements

- Mobile app development
- Advanced analytics and ML predictions
- Integration with smart home systems
- Multi-tenant architecture
- Advanced reporting features
