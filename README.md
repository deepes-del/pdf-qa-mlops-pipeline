# 🤖 PDF Q&A MLOps Pipeline

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-20.10+-blue.svg)](https://docker.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![Kafka](https://img.shields.io/badge/Apache%20Kafka-2.8+-orange.svg)](https://kafka.apache.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A **production-ready PDF Question & Answer application** built with comprehensive **MLOps practices**. Upload PDFs, ask questions using AI, and monitor everything in real-time with enterprise-grade observability.

## ✨ Key Features

- 🔍 **Intelligent PDF Q&A**: Extract text and answer questions using Google Gemini AI
- 📊 **Real-time Event Streaming**: Apache Kafka for event-driven architecture
- 🔧 **MLOps Pipeline**: Complete CI/CD with Jenkins, testing, and deployment
- 📈 **Monitoring & Observability**: Prometheus metrics, Grafana dashboards
- 🧪 **Experiment Tracking**: MLflow for model versioning and metadata
- 🐳 **Containerized Deployment**: Docker and Docker Compose for scalability
- 🔒 **Production Ready**: Structured logging, error handling, security scans

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │     Kafka       │    │   Prometheus    │
│   Frontend      │───▶│   Event Bus     │───▶│   Monitoring    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PDF Q&A       │    │   Event         │    │    Grafana      │
│   Application   │    │   Consumer      │    │   Dashboard     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                             │
         ▼                                             ▼
┌─────────────────┐                        ┌─────────────────┐
│    MLflow       │                        │    Jenkins      │
│   Tracking      │                        │    CI/CD        │
└─────────────────┘                        └─────────────────┘
```

## 🛠️ Technology Stack

### **Core Technologies**
| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Frontend** | Streamlit | 1.28+ | Interactive web interface |
| **AI/ML** | Google Gemini API | Latest | Large Language Model for Q&A |
| **Vector Processing** | NumPy | 1.24+ | Embedding computations |
| **PDF Processing** | PyPDF2 | 3.0+ | Text extraction from PDFs |

### **MLOps Infrastructure**
| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Event Streaming** | Apache Kafka | 2.8+ | Real-time event processing |
| **Monitoring** | Prometheus | Latest | Metrics collection |
| **Visualization** | Grafana | Latest | Dashboards and alerts |
| **Experiment Tracking** | MLflow | 2.8+ | Model versioning and metadata |
| **CI/CD** | Jenkins | Latest | Automated testing and deployment |

### **DevOps & Infrastructure**
| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Containerization** | Docker | 20.10+ | Application packaging |
| **Orchestration** | Docker Compose | 2.0+ | Multi-service deployment |
| **Testing** | pytest | Latest | Unit and integration testing |
| **Code Quality** | flake8, black, bandit | Latest | Linting, formatting, security |
| **Package Management** | pip | Latest | Python dependencies |

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Google Gemini API Key
- Jenkins (for CI/CD)

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/pdf-qa-mlops-pipeline.git
cd pdf-qa-mlops-pipeline
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
# Add your Google Gemini API key and other settings
```

### 3. Start MLOps Stack

```bash
# Start all services (Kafka, Prometheus, Grafana, MLflow, App)
docker-compose up -d

# Verify all services are running
docker-compose ps
```

### 4. Access Applications

| Service | URL | Credentials |
|---------|-----|-------------|
| **PDF Q&A App** | http://localhost:8501 | Enter Gemini API key |
| **Kafka UI** | http://localhost:8081 | No authentication |
| **Prometheus** | http://localhost:9090 | No authentication |
| **Grafana** | http://localhost:3000 | admin / admin123 |
| **MLflow** | http://localhost:5000 | No authentication |

### 5. Using the Application

1. **Open** http://localhost:8501 in your browser
2. **Enter your Google Gemini API key** in the input field
3. **Upload a PDF file** using the file uploader
4. **Wait for processing** (text extraction and embedding generation)
5. **Ask questions** about the PDF content
6. **Monitor events** in real-time at http://localhost:8081

## 📊 Monitoring

### Prometheus Metrics

The application exposes the following metrics:

- `pdf_qa_requests_total`: Total number of Q&A requests
- `pdf_qa_request_duration_seconds`: Request processing time
- `pdf_qa_active_sessions`: Number of active sessions
- `pdf_processing_duration_seconds`: PDF processing time
- `embedding_generation_duration_seconds`: Embedding generation time

### Kafka Events

Events are published to the following topics:

- `pdf_processing`: PDF upload and processing events
- `embedding_generation`: Text embedding creation events
- `query_processing`: Question processing and retrieval events
- `answer_generation`: Answer generation events

### Grafana Dashboards

Access Grafana at http://localhost:3000 to view:

- Application performance metrics
- System resource utilization
- Event processing rates
- Error rates and alerts

## 🔄 CI/CD Pipeline

The Jenkins pipeline includes:

1. **Code Quality**: Linting, formatting, security scans
2. **Testing**: Unit tests, integration tests, performance tests
3. **Build**: Docker image creation and security scanning
4. **Deploy**: Automated deployment to staging/production
5. **Validation**: Model performance validation
6. **Tracking**: MLflow experiment logging

### Pipeline Stages

```yaml
Checkout → Quality Checks → Tests → Build → Security Scan → Deploy → Validate
```

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run unit tests
pytest tests/test_app.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## 📈 MLflow Experiment Tracking

The application automatically logs:

- Model parameters (chunk size, overlap, top-k)
- Performance metrics
- Deployment metadata
- Git commit information
- Docker image tags

Access MLflow UI at http://localhost:5000 to view experiments.

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
GEMINI_API_KEY=your_api_key
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
MLFLOW_TRACKING_URI=http://localhost:5000
LOG_LEVEL=INFO
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RETRIEVAL=3
```

### Application Settings

Modify `app.py` to adjust:

- Embedding model (`models/text-embedding-004`)
- LLM model (`gemini-1.5-flash`)
- Chunking parameters
- Retrieval settings

## 🐛 Troubleshooting

### Common Issues

1. **Kafka Connection Failed**
   ```bash
   # Check Kafka status
   docker-compose logs kafka
   
   # Restart Kafka services
   docker-compose restart kafka zookeeper
   ```

2. **Prometheus Metrics Not Showing**
   ```bash
   # Check metrics endpoint
   curl http://localhost:8000/metrics
   
   # Verify Prometheus config
   docker-compose logs prometheus
   ```

3. **MLflow Not Accessible**
   ```bash
   # Check MLflow logs
   docker-compose logs mlflow
   
   # Restart MLflow
   docker-compose restart mlflow
   ```

## 📝 Development

### Adding New Features

1. Update `app.py` with new functionality
2. Add corresponding tests in `tests/`
3. Update Prometheus metrics if needed
4. Add Kafka events for new operations
5. Update documentation

### Code Quality

```bash
# Format code
black app.py

# Lint code
flake8 app.py --max-line-length=100

# Security scan
bandit -r app.py
```

## 🚀 Production Deployment

### Kubernetes Deployment

```bash
# Build and push image
docker build -t your-registry/pdf-qa-app:latest .
docker push your-registry/pdf-qa-app:latest

# Deploy with Helm
helm upgrade --install pdf-qa ./helm-chart \
  --set image.tag=latest \
  --set environment=production
```

### Scaling Considerations

- Use Kafka partitioning for high throughput
- Implement Redis caching for embeddings
- Use load balancers for multiple app instances
- Configure auto-scaling based on metrics

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Run quality checks
5. Submit a pull request

## 📞 Support

For issues and questions:

- Create an issue in the repository
- Check the troubleshooting section
- Review logs in Docker Compose services
