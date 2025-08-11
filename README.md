# 🛰️ Satellite Interlink Communication Analyzer

A comprehensive Python web application for analyzing interlink communication windows between two satellites, taking into account Earth obstruction and orbital mechanics.

## 🌟 Features

- **TLE Processing**: Upload and process Two-Line Element (TLE) data for satellites
- **Orbital Calculations**: Advanced orbital mechanics using the `ephem` library
- **Earth Obstruction Detection**: Accounts for Earth blocking line-of-sight between satellites
- **3D Visualization**: Interactive 3D visualization using Three.js
- **Communication Windows**: Calculate optimal communication time windows
- **Modern Web Interface**: Responsive design with Bootstrap and custom CSS
- **Real-time Analysis**: Dynamic calculation of satellite positions and visibility

## 🏗️ Architecture

- **Backend**: Flask Python web framework
- **Frontend**: HTML5, CSS3, JavaScript with Three.js for 3D graphics
- **Orbital Mechanics**: PyEphem library for satellite position calculations
- **Containerization**: Docker for easy deployment
- **Cloud Ready**: AWS ECS deployment configuration included

## 📋 Prerequisites

- Python 3.9+
- Docker (for containerized deployment)
- AWS CLI (for AWS deployment)
- Modern web browser with WebGL support

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd satellite-interlink
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:5000`

### Using Docker

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Or build and run manually**
   ```bash
   docker build -t satellite-interlink .
   docker run -p 5000:5000 satellite-interlink
   ```

## 📊 Usage

### 1. Input Satellite Data
- Enter satellite names
- Provide TLE Line 1 and Line 2 for each satellite
- Set analysis time period (start and end dates)

### 2. Calculate Interlink Windows
- Click "Calculate Interlink Windows"
- The system will process TLE data and calculate communication opportunities

### 3. View Results
- **3D Visualization**: Interactive Earth view with satellite positions
- **Results Summary**: Total communication windows and status
- **Detailed Table**: Timestamp, distance, and position data for each window

### 4. Interact with Visualization
- **Mouse Controls**: Click and drag to rotate view
- **Zoom**: Use mouse wheel to zoom in/out
- **Satellite Labels**: Hover over satellites for information

## 🔧 Technical Details

### Orbital Calculations

The application uses the SGP4/SDP4 orbital propagation models through the `ephem` library:

- **Position Calculation**: Computes satellite positions at specific times
- **Distance Calculation**: Haversine formula for ground track distances
- **Earth Obstruction**: Simplified model checking line-of-sight blockage
- **Communication Range**: Configurable maximum communication distance (default: 1000 km)

### Earth Obstruction Model

The current implementation uses a simplified heuristic:
- For Low Earth Orbit (LEO) satellites: Maximum distance of 2000 km
- More sophisticated models can be implemented for higher accuracy

### Performance Considerations

- **Time Step**: Default 5-minute intervals for calculations
- **Optimization**: Efficient orbital propagation algorithms
- **Scalability**: Designed for real-time analysis of multiple satellites

## 🚀 AWS Deployment

### Prerequisites
- AWS CLI configured with appropriate permissions
- Docker running locally
- ECS Task Execution Role (create if needed)

### Deploy to AWS

1. **Make deployment script executable**
   ```bash
   chmod +x aws-deploy.sh
   ```

2. **Run deployment**
   ```bash
   ./aws-deploy.sh
   ```

3. **Access your application**
   - Navigate to AWS ECS Console
   - Find your service and note the public IP
   - Access via `http://<PUBLIC_IP>:5000`

### AWS Resources Created

- **ECR Repository**: Container image storage
- **ECS Cluster**: Container orchestration
- **ECS Service**: Application deployment
- **Security Group**: Network access control
- **CloudWatch Logs**: Application logging

## 🧪 Testing

### Sample TLE Data

The application comes with sample TLE data for testing:

**ISS (International Space Station)**
```
1 25544U 98067A   24001.50000000  .00012227  00000+0  22906-3 0  9999
2 25544  51.6400 114.3973 0001263 255.8500 104.1500 15.50000000 00000+0
```

**STARLINK-1234 (Sample Starlink)**
```
1 44713U 19074A   24001.50000000  .00000000  00000+0  00000+0 0  9999
2 44713  52.9979 288.0000 0001263 180.0000 180.0000 15.05425952 00000+0
```

### Validation

- TLE format validation
- Date range validation
- Orbital parameter sanity checks

## 🔒 Security

- Non-root Docker container
- Input validation and sanitization
- CORS configuration for web security
- Health checks and monitoring

## 📈 Monitoring and Logging

- **Health Checks**: Application health monitoring
- **CloudWatch Integration**: AWS-native logging
- **Error Handling**: Comprehensive error reporting
- **Performance Metrics**: Response time and throughput

## 🛠️ Development

### Project Structure
```
satellite-interlink/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Local development
├── aws-deploy.sh        # AWS deployment script
├── templates/            # HTML templates
│   └── index.html       # Main application page
├── static/              # Static assets
│   ├── css/            # Stylesheets
│   │   └── style.css   # Main CSS
│   └── js/             # JavaScript
│       └── app.js      # Main application logic
└── README.md            # This file
```

### Adding Features

1. **New Orbital Models**: Extend the `Satellite` class
2. **Enhanced Visualization**: Modify Three.js scene in `app.js`
3. **Additional Calculations**: Add new endpoints in `app.py`
4. **UI Improvements**: Update HTML templates and CSS

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **PyEphem**: Orbital mechanics calculations
- **Three.js**: 3D visualization library
- **Flask**: Web framework
- **Bootstrap**: UI components

## 📞 Support

For questions and support:
- Create an issue in the repository
- Check the documentation
- Review the code comments

---

**Built with ❤️ for the satellite communication community**
