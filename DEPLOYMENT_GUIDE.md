# Adobe Finale PDF Reader - Deployment Guide

## 🚀 Quick Deployment

### Option 1: Docker (Recommended)

1. **Build the Docker image**
   ```bash
   docker build --platform linux/amd64 -t adobe-finale-pdf-reader .
   ```

2. **Run with basic configuration**
   ```bash
   docker run -p 8080:8080 adobe-finale-pdf-reader
   ```

3. **Access the application**
   - Open http://localhost:8080 in your browser
   - The application will work with basic features (no LLM/TTS)

### Option 2: With AI Features

1. **Configure environment variables**
   ```bash
   # For Gemini LLM
   export LLM_PROVIDER=gemini
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
   export GEMINI_MODEL=gemini-2.5-flash
   
   # For Azure TTS
   export TTS_PROVIDER=azure
   export AZURE_TTS_KEY=your-azure-tts-key
   export AZURE_TTS_ENDPOINT=your-azure-tts-endpoint
   ```

2. **Run with AI features**
   ```bash
   docker run \
     -e LLM_PROVIDER=gemini \
     -e GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json \
     -e GEMINI_MODEL=gemini-2.5-flash \
     -e TTS_PROVIDER=azure \
     -e AZURE_TTS_KEY=your-azure-tts-key \
     -e AZURE_TTS_ENDPOINT=your-azure-tts-endpoint \
     -p 8080:8080 \
     adobe-finale-pdf-reader
   ```

## ☁️ Cloud Deployment

### AWS Deployment

1. **Deploy to ECS**
   ```bash
   # Create ECR repository
   aws ecr create-repository --repository-name adobe-finale-pdf-reader
   
   # Tag and push image
   docker tag adobe-finale-pdf-reader:latest your-account.dkr.ecr.region.amazonaws.com/adobe-finale-pdf-reader:latest
   aws ecr get-login-password --region region | docker login --username AWS --password-stdin your-account.dkr.ecr.region.amazonaws.com
   docker push your-account.dkr.ecr.region.amazonaws.com/adobe-finale-pdf-reader:latest
   ```

2. **Create ECS Task Definition**
   ```json
   {
     "family": "adobe-finale-pdf-reader",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "512",
     "memory": "1024",
     "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "adobe-finale-pdf-reader",
         "image": "your-account.dkr.ecr.region.amazonaws.com/adobe-finale-pdf-reader:latest",
         "portMappings": [
           {
             "containerPort": 8080,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "LLM_PROVIDER",
             "value": "gemini"
           },
           {
             "name": "TTS_PROVIDER",
             "value": "azure"
           }
         ],
         "secrets": [
           {
             "name": "GOOGLE_APPLICATION_CREDENTIALS",
             "valueFrom": "arn:aws:secretsmanager:region:account:secret:google-credentials"
           },
           {
             "name": "AZURE_TTS_KEY",
             "valueFrom": "arn:aws:secretsmanager:region:account:secret:azure-tts-key"
           }
         ]
       }
     ]
   }
   ```

### Azure Deployment

1. **Deploy to Container Instances**
   ```bash
   # Create resource group
   az group create --name adobe-finale-rg --location eastus
   
   # Create container registry
   az acr create --resource-group adobe-finale-rg --name adobefinaleregistry --sku Basic
   
   # Build and push image
   az acr build --registry adobefinaleregistry --image adobe-finale-pdf-reader .
   
   # Deploy container instance
   az container create \
     --resource-group adobe-finale-rg \
     --name adobe-finale-container \
     --image adobefinaleregistry.azurecr.io/adobe-finale-pdf-reader:latest \
     --dns-name-label adobe-finale-app \
     --ports 8080 \
     --environment-variables LLM_PROVIDER=gemini TTS_PROVIDER=azure
   ```

### Google Cloud Deployment

1. **Deploy to Cloud Run**
   ```bash
   # Build and push to Container Registry
   gcloud builds submit --tag gcr.io/PROJECT_ID/adobe-finale-pdf-reader
   
   # Deploy to Cloud Run
   gcloud run deploy adobe-finale-pdf-reader \
     --image gcr.io/PROJECT_ID/adobe-finale-pdf-reader \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8080 \
     --set-env-vars LLM_PROVIDER=gemini,TTS_PROVIDER=azure
   ```

## 🔧 Environment Configuration

### LLM Providers

#### OpenAI
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o
```

#### Gemini
```bash
LLM_PROVIDER=gemini
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GEMINI_MODEL=gemini-2.5-flash
```

#### Azure OpenAI
```bash
LLM_PROVIDER=azure
AZURE_OPENAI_KEY=your-azure-openai-key
AZURE_OPENAI_BASE=https://your-resource.openai.azure.com/
AZURE_API_VERSION=2024-02-15-preview
AZURE_DEPLOYMENT_NAME=gpt-4o
```

#### Ollama (Local)
```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

### TTS Providers

#### Azure Text-to-Speech
```bash
TTS_PROVIDER=azure
AZURE_TTS_KEY=your-azure-tts-key
AZURE_TTS_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
```

## 📊 Performance Optimization

### Resource Requirements

- **CPU**: 1-2 cores (512-1024 CPU units)
- **Memory**: 1-2 GB RAM
- **Storage**: 2-5 GB (for temporary PDF processing)
- **Network**: Standard internet connectivity

### Scaling Configuration

#### Horizontal Scaling
```bash
# For Kubernetes
kubectl scale deployment adobe-finale-pdf-reader --replicas=3

# For ECS
aws ecs update-service --cluster your-cluster --service adobe-finale-service --desired-count 3
```

#### Vertical Scaling
```bash
# Increase CPU and memory in task definition
"cpu": "1024",
"memory": "2048"
```

## 🔒 Security Configuration

### SSL/TLS Setup

1. **Obtain SSL Certificate**
   ```bash
   # Using Let's Encrypt
   certbot certonly --standalone -d your-domain.com
   ```

2. **Configure Nginx Reverse Proxy**
   ```nginx
   server {
       listen 443 ssl;
       server_name your-domain.com;
       
       ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
       
       location / {
           proxy_pass http://localhost:8080;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Environment Variable Security

1. **Use Secret Management**
   ```bash
   # AWS Secrets Manager
   aws secretsmanager create-secret --name google-credentials --secret-string file://credentials.json
   
   # Azure Key Vault
   az keyvault secret set --vault-name your-vault --name google-credentials --file credentials.json
   ```

2. **Rotate Credentials Regularly**
   ```bash
   # Update secrets
   aws secretsmanager update-secret --secret-id google-credentials --secret-string file://new-credentials.json
   ```

## 📈 Monitoring and Logging

### Health Checks

The application includes built-in health checks:
```bash
# Check application health
curl http://localhost:8080/health

# Docker health check
docker inspect adobe-finale-pdf-reader | grep Health -A 10
```

### Logging Configuration

1. **Application Logs**
   ```bash
   # View container logs
   docker logs adobe-finale-pdf-reader
   
   # Follow logs
   docker logs -f adobe-finale-pdf-reader
   ```

2. **Structured Logging**
   ```json
   {
     "timestamp": "2024-01-27T10:30:00Z",
     "level": "INFO",
     "message": "PDF processing completed",
     "document_id": "doc_20240127_103000_sample.pdf",
     "processing_time": 2.5
   }
   ```

## 🧪 Testing Deployment

### Smoke Tests

1. **Health Check**
   ```bash
   curl -f http://localhost:8080/ || echo "Health check failed"
   ```

2. **API Endpoints**
   ```bash
   # Test API info
   curl http://localhost:8080/api
   
   # Test documents endpoint
   curl http://localhost:8080/api/documents
   ```

3. **Frontend Access**
   ```bash
   # Check if React app loads
   curl -I http://localhost:8080/
   ```

### Load Testing

```bash
# Using Apache Bench
ab -n 100 -c 10 http://localhost:8080/

# Using wrk
wrk -t12 -c400 -d30s http://localhost:8080/
```

## 🚨 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using port 8080
   lsof -i :8080
   
   # Kill process or use different port
   docker run -p 8081:8080 adobe-finale-pdf-reader
   ```

2. **Memory Issues**
   ```bash
   # Increase Docker memory limit
   docker run --memory=2g adobe-finale-pdf-reader
   ```

3. **Environment Variables Not Set**
   ```bash
   # Check environment variables
   docker exec adobe-finale-pdf-reader env | grep LLM
   ```

### Debug Mode

```bash
# Run with debug logging
docker run -e LOG_LEVEL=DEBUG adobe-finale-pdf-reader

# Access container shell
docker exec -it adobe-finale-pdf-reader /bin/bash
```

## 📋 Pre-Demo Checklist

- [ ] Application builds successfully
- [ ] All environment variables configured
- [ ] SSL certificate installed (if using custom domain)
- [ ] Health checks passing
- [ ] Sample PDFs ready for testing
- [ ] Demo script prepared
- [ ] Backup deployment ready
- [ ] Monitoring configured
- [ ] Performance tested

## 🎯 Adobe Finale Demo Preparation

### Demo Flow

1. **Introduction** (30 seconds)
   - Show the application interface
   - Explain the "From Brains to Experience" concept

2. **PDF Upload** (1 minute)
   - Upload a sample PDF
   - Show real-time processing
   - Demonstrate persona detection

3. **Core Features** (2 minutes)
   - Navigate through PDF with Adobe Embed API
   - Show related section detection
   - Demonstrate position tracking

4. **AI Features** (2 minutes)
   - Generate insights
   - Show persona-specific recommendations
   - Create audio podcast

5. **Technical Highlights** (1 minute)
   - Show performance metrics
   - Demonstrate offline capabilities
   - Highlight scalability

### Demo Tips

- **Prepare Sample PDFs**: Use documents that showcase different personas
- **Practice Timing**: Keep demo under 7 minutes
- **Have Backup**: Prepare offline demo if internet fails
- **Show Innovation**: Highlight unique features and technical excellence
- **Be Ready for Questions**: Prepare answers about architecture and scalability

---

**Ready for Adobe Finale! 🚀**
