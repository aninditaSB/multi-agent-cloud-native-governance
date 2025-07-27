# AI Quality Monitoring Demo with Cloud-Native Stack

A demonstration system implementing AI quality monitoring and governance infrastructure using modern cloud-native technologies.

## Architecture

- **FastAPI Service**: AI processing simulation with realistic metrics
- **Prometheus**: Real-time metrics collection and monitoring
- **Grafana**: Live visualization dashboards
- **Kubernetes**: Container orchestration and scaling
- **Istio**: Service mesh integration

## Metrics Collected

- `agent_helpfulness_score` - AI response quality scoring
- `agent_transparency_score` - Response clarity assessment  
- `agent_requests_total` - Request volume tracking

## Quick Start

### Deploy to Minikube

Build and deploy all services
eval $(minikube docker-env)
docker build -t multi-agent-demo:latest .
kubectl apply -f deployment.yaml

Wait for deployment
kubectl wait --for=condition=available --timeout=300s deployment/multi-agent-demo
kubectl wait --for=condition=available --timeout=300s deployment/prometheus
kubectl wait --for=condition=available --timeout=300s deployment/grafana

Access services
kubectl port-forward service/multi-agent-demo-service 8080:8080 &
kubectl port-forward service/prometheus-service 9090:9090 &
kubectl port-forward service/grafana-service 3000:3000 &

text

### Test the System

Health check
curl "http://localhost:8080/health"

Process text input
curl -X POST "http://localhost:8080/orchestrate"
-H "Content-Type: application/json"
-d '{"text": "Analyze this input text"}'

View metrics
curl "http://localhost:8080/metrics"

text

## Access Points

- **API Service**: http://localhost:8080
- **Prometheus**: http://localhost:9090  
- **Grafana**: http://localhost:3000 (admin/admin)

## Key Features

**Infrastructure**
- Complete Kubernetes deployment with multi-service orchestration
- Integrated Prometheus monitoring with custom metrics
- Real-time Grafana dashboards with live data updates
- Istio service mesh for enhanced networking and observability

**Monitoring Capabilities**
- Live quality score tracking and visualization
- Request volume and performance metrics
- Health monitoring and alerting capabilities
- Time-series data collection for trend analysis

**Cloud-Native Patterns**
- Microservices architecture with proper separation of concerns
- Container-based deployment with resource management
- Service discovery and load balancing
- Scalable monitoring and observability stack

## API Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/` | GET | Service information |
| `/health` | GET | Health status |
| `/orchestrate` | POST | Text processing |
| `/metrics` | GET | Prometheus metrics |

## Dashboard Setup

1. Access Grafana at http://localhost:3000
2. Add Prometheus data source: `http://prometheus-service:9090`
3. Create panels with queries:
   - `agent_helpfulness_score`
   - `agent_transparency_score`
   - `rate(agent_requests_total[1m])`

## Technology Stack

- **FastAPI** - High-performance web framework
- **Prometheus** - Metrics collection and alerting
- **Grafana** - Data visualization and dashboards
- **Kubernetes** - Container orchestration
- **Istio** - Service mesh networking
- **Docker** - Containerization

## Use Cases
- Monitoring infrastructure testing and validation
- Cloud-native architecture prototyping
- AI governance framework development
- Observability stack implementation


