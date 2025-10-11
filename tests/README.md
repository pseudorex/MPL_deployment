# MPL System K6 Load Tests ⚡

**Ultra-Fast Load Testing Suite** - Complete system testing in **2 minutes total** with up to 150+ concurrent users!

This directory contains clean, fast K6 load testing scripts for the MPL (Multi-Player League) FastAPI system. Each test runs for exactly **30 seconds** with realistic performance expectations.

## 📁 Test Files (All 30 seconds each)

### 🚀 Fast Individual Tests
- **`team_endpoints_test.js`** - 📅 **100 users, 30s** - Tests `/teamquestions` endpoints
- **`mystery_test.js`** - 🔮 **80 users, 30s** - Tests `/mystery` endpoints  
- **`admin_test.js`** - 🔧 **60 users, 30s** - Tests all `/admin/*` endpoints

### 🎯 Complete System Test
- **`complete_system_test.js`** - 🔥 **150 users, 30s** - Full system testing with mixed workflows

## 🚀 Prerequisites

1. **Install K6**: Download from [k6.io](https://k6.io/docs/getting-started/installation/)
2. **Start your FastAPI server**: Make sure your MPL API is running on `http://localhost:8000`
3. **Database**: Ensure your database is set up and accessible

## ⚡ Running Tests (All 30 seconds each)

### 🚀 Individual Endpoint Tests
```bash
# Test team creation and assignment (100 users)
k6 run team_endpoints_test.js

# Test mystery operations (80 users)
k6 run mystery_test.js

# Test admin operations (60 users)
k6 run admin_test.js
```

### 🎯 Complete System Test
```bash
# Test entire system with mixed workflows (150 users)
k6 run complete_system_test.js
```

### 🏁 Run All Tests (2 minutes total)
```bash
# Complete system coverage in 2 minutes
k6 run team_endpoints_test.js     # 30s
k6 run mystery_test.js            # 30s  
k6 run admin_test.js              # 30s
k6 run complete_system_test.js    # 30s
```

### Custom Configuration

You can override the base URL and other settings:

```bash
# Test against a different server
k6 run -e BASE_URL=http://your-server:8000/siamMPL comprehensive_load_test.js

# Run with custom VU count and duration
k6 run --vus 20 --duration 5m team_endpoints_test.js
```

## 📊 Test Scenarios (All 30 seconds)

### 📅 Team Endpoints Test (100 users)
- **Focus**: Team creation and question assignment
- **Load**: 100 concurrent users
- **Duration**: 30 seconds
- **Tests**: POST `/teamquestions/`, question creation

### 🔮 Mystery Test (80 users)
- **Focus**: Mystery question operations
- **Load**: 80 concurrent users  
- **Duration**: 30 seconds
- **Tests**: PUT `/mystery/`, DELETE `/mystery/quit`

### 🔧 Admin Test (60 users)
- **Focus**: Administrative operations
- **Load**: 60 concurrent users
- **Duration**: 30 seconds
- **Tests**: All `/admin/*` endpoints (GET, POST, PUT)

### 🎯 Complete System Test (150 users)
- **Focus**: Full system integration
- **Load**: 150 concurrent users
- **Duration**: 30 seconds
- **Tests**: Mixed workflows across all endpoints

## 🎯 Test Coverage

### Team Operations
- Create teams with assigned questions
- Handle duplicate team creation attempts
- Validate question assignments

### Mystery Operations  
- Assign mystery questions to teams
- Handle insufficient points scenarios
- Quit mystery questions
- Validate difficulty-based question allocation

### Admin Operations
- **Teams**: CRUD operations, points management
- **Questions**: Create and retrieve questions  
- **Mystery Questions**: Full CRUD with status management
- **Team-Question Mappings**: Delete operations

### System Integration
- Mixed user workflows
- Concurrent operations
- Data consistency validation
- Error handling under load

## 📈 Performance Thresholds

The tests include the following performance expectations:

- **Response Time**: 95% of requests < 500ms (Load), < 1000ms (Stress)
- **Error Rate**: < 10% (Load), < 20% (Stress)
- **Throughput**: Monitored automatically by K6

## 🔧 Customization

### Modify Test Data
Edit `config.js` to customize:
- Question templates
- Team name patterns
- Points ranges
- Difficulty levels

### Adjust Load Patterns
Update the `options` export in any test file:

```javascript
export let options = {
  stages: [
    { duration: '30s', target: 5 },   // Ramp up
    { duration: '2m', target: 5 },    // Stay at 5 users
    { duration: '30s', target: 0 },   // Ramp down
  ],
};
```

### Custom Validation
Modify the `validateResponse` function in `config.js` to add custom checks.

## 🐛 Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure FastAPI server is running
   - Check the BASE_URL in config.js

2. **Database Errors**
   - Verify database connectivity
   - Check for proper table creation

3. **High Error Rates**
   - Reduce concurrent users
   - Check server resource utilization
   - Review application logs

### Debug Mode

Add verbose logging to any test:

```javascript
export let options = {
  // ... your config
  console: {
    level: 'debug'
  }
};
```

## 📝 Test Results

K6 outputs detailed metrics including:
- Request rates and response times
- Error rates by endpoint
- Resource utilization patterns
- Custom check pass/fail rates

Results can be exported to various formats:
```bash
# Export to JSON
k6 run --out json=test_results.json comprehensive_load_test.js

# Export to InfluxDB
k6 run --out influxdb=http://localhost:8086/k6 comprehensive_load_test.js
```

## 🔄 Continuous Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Run Load Tests
  run: |
    k6 run --quiet --no-color comprehensive_load_test.js
```

## 📞 Support

For issues with the tests or suggestions for improvements, please refer to the main project documentation or create an issue in the project repository.

---

**Happy Load Testing! 🚀**
