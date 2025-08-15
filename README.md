# 🚀 Standup Bot

An AI-powered Slack bot that revolutionizes daily standups by automating the entire process. Instead of scheduling synchronous meetings, this bot collects responses asynchronously from team members and generates intelligent summaries using LangGraph and OpenAI.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Development Setup](#development-setup)
- [Deployment](#deployment)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- **🤖 AI-Powered Summaries**: Intelligent standup summaries using OpenAI and LangGraph that extract key insights and action items
- **⏰ Flexible Scheduling**: Set custom standup times that work for your team's timezone and schedule
- **📱 Asynchronous Collection**: Team members respond at their own pace via Slack DMs - no need for everyone to be online simultaneously
- **📊 Smart Channel Integration**: Automatically post summaries to any Slack channel of your choice
- **🔄 Automated Workflow**: Once configured, the bot runs completely autonomously - no manual intervention needed
- **🌍 Timezone Support**: Handles multiple timezones for distributed teams
- **🔐 Secure OAuth**: Secure Slack workspace integration with proper authentication
- **📈 Scalable Architecture**: Microservices design that grows with your team

## 🏗️ Architecture

The project follows a microservices architecture designed for reliability and scalability. Here's how the automation works:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Server      │    │   Scheduler     │
│   (Next.js)     │◄──►│   (Flask)       │◄──►│   (Celery)      │
│   Setup UI      │    │   + LangGraph   │    │   Cron Jobs     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MongoDB       │    │     Redis       │    │     Slack       │
│   (Workspaces,  │    │   (Task Queue,  │    │   (DMs, Events, │
│    Responses,   │    │    Schedules)   │    │    Posts)       │
│    Preferences) │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘

Workflow:
1. Scheduler (Celery) → Server (LangGraph) → Slack (DMs)
2. Slack (Responses) → Server (Event Handler) → MongoDB
3. Server (LangGraph) → OpenAI → Slack (Summary Post)
```

### Components

- **Frontend**: Next.js 15 with TypeScript and Tailwind CSS for easy setup and configuration
- **Backend Server**: Flask API with Slack SDK integration handling all Slack interactions
- **Scheduler**: Celery worker that automatically triggers standups at scheduled times
- **Database**: MongoDB for storing workspace data, user responses, and standup history
- **Cache/Queue**: Redis for managing asynchronous task processing and response collection
- **AI Engine**: LangGraph orchestrates the workflow from collection to summary generation

## 🔄 How It Works

### The Automated Standup Process

1. **🕐 Scheduled Trigger**: The scheduler automatically initiates standups at your configured time
2. **📱 Individual Outreach**: The bot sends personalized DMs to each team member asking for their standup
3. **⏳ Asynchronous Responses**: Team members respond at their convenience - no pressure to be online simultaneously
4. **🤖 AI Processing**: LangGraph collects all responses and processes them through OpenAI
5. **📊 Smart Summary**: AI generates a comprehensive summary highlighting key updates, blockers, and action items
6. **📢 Channel Posting**: The summary is automatically posted to your chosen Slack channel

### Why This Matters

**⏰ Saves Time**: No more scheduling conflicts or waiting for everyone to join a meeting. Team members can respond when it works for them.

**🌍 Works Globally**: Perfect for distributed teams across different timezones. No one needs to wake up early or stay up late for standups.

**📈 Improves Engagement**: Asynchronous responses often lead to more thoughtful, detailed updates compared to rushed verbal responses.

**🤖 Reduces Manual Work**: Once set up, the entire process runs automatically. No need for someone to manually collect and summarize responses.

**📊 Better Insights**: AI-powered summaries extract key themes, identify blockers, and highlight action items that might be missed in verbal standups.

**💡 Flexible Format**: Team members can provide detailed responses without worrying about time constraints or interrupting others.

## 🛠️ Tech Stack

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **React 19** - Latest React features

### Backend
- **Flask** - Python web framework
- **FastAPI** - High-performance API framework
- **LangGraph** - AI workflow orchestration
- **LangChain** - LLM application framework
- **Slack SDK** - Official Slack API client

### Infrastructure
- **Docker** - Containerization
- **Kubernetes** - Container orchestration
- **MongoDB** - NoSQL database
- **Redis** - In-memory data store
- **Celery** - Distributed task queue

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js 18+** and npm
- **Python 3.9+** and pip
- **Docker** and Docker Compose
- **Kubernetes** (for production deployment)
- **MongoDB** (local or cloud instance)
- **Redis** (local or cloud instance)

### Required API Keys

- **Slack App Credentials**:
  - Client ID
  - Client Secret
  - Signing Secret
- **OpenAI API Key**

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd standup-bot
```

### 2. Set Up Environment Variables

```bash
cp env.example .env
```

Edit `.env` with your actual credentials:

```env
# Slack Configuration
SLACK_CLIENT_ID=your_slack_client_id
SLACK_CLIENT_SECRET=your_slack_client_secret
SLACK_SIGNING_SECRET=your_slack_signing_secret

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Application URLs
BASE_URL=http://localhost:4000
FRONTEND_URL=http://localhost:3000

# Database Configuration
MONGODB_URI=mongodb://localhost:27017/standup_bot

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
```

### 3. Start Services with Docker Compose

```bash
# Start all services
docker-compose up -d

# Or start individual services
docker-compose up -d mongodb redis
docker-compose up -d server scheduler
docker-compose up -d frontend
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:4000
- **MongoDB**: mongodb://localhost:27017
- **Redis**: redis://localhost:6379

## 💻 Development Setup

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Backend Development

```bash
cd server
pip install -r requirements.txt
python app.py
```

### Scheduler Development

```bash
cd schedular
pip install -r requirements.txt
celery -A celery_app worker --loglevel=info
```

### Database Setup

```bash
# Initialize MongoDB collections
cd server
python -c "from db.init_db import init_database; init_database()"
```

## 🚀 Deployment

### Kubernetes Deployment

1. **Build and Load Docker Images**:

```bash
./deploy.sh
```

2. **Update Secrets** (if not already done):

```bash
# Generate base64 encoded secrets
echo -n 'your-slack-client-id' | base64
echo -n 'your-slack-client-secret' | base64
echo -n 'your-slack-signing-secret' | base64
echo -n 'your-openai-api-key' | base64
```

3. **Update `k8s/secrets.yaml`** with the generated values.

4. **Apply Kubernetes Configurations**:

```bash
kubectl apply -f k8s/
```

5. **Check Deployment Status**:

```bash
kubectl get pods
kubectl get services
```

### Docker Deployment

```bash
# Build images
docker build -t standup-server:latest ./server
docker build -t standup-frontend:latest ./frontend
docker build -t standup-scheduler:latest ./schedular

# Run containers
docker run -d --name mongodb mongo:latest
docker run -d --name redis redis:latest
docker run -d --name standup-server standup-server:latest
docker run -d --name standup-scheduler standup-scheduler:latest
docker run -d --name standup-frontend standup-frontend:latest
```

## ⚙️ Configuration

### Slack App Setup

1. Create a new Slack app at https://api.slack.com/apps
2. Configure OAuth & Permissions:
   - `chat:write` - Send messages
   - `im:write` - Send direct messages
   - `channels:read` - Read channel information
   - `users:read` - Read user information
3. Configure Event Subscriptions:
   - Subscribe to bot events: `message.im`
4. Set up OAuth redirect URLs:
   - `http://localhost:4000/slack/oauth/callback` (development)
   - `https://your-domain.com/slack/oauth/callback` (production)

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SLACK_CLIENT_ID` | Slack app client ID | Yes |
| `SLACK_CLIENT_SECRET` | Slack app client secret | Yes |
| `SLACK_SIGNING_SECRET` | Slack app signing secret | Yes |
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `MONGODB_URI` | MongoDB connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `BASE_URL` | Backend server URL | Yes |
| `FRONTEND_URL` | Frontend application URL | Yes |

## 📚 API Documentation

### Authentication Endpoints

- `GET /slack/install` - Redirect to Slack OAuth
- `GET /slack/oauth/callback` - Handle OAuth callback
- `POST /slack/events` - Handle Slack events

### Workspace Management

- `GET /api/channels/{workspace_id}` - Get available channels
- `POST /api/channels/{workspace_id}` - Set channel preferences
- `GET /api/workspace/{workspace_id}/channel` - Get current channel

### Standup Management

- `POST /api/standup/start` - Start a new standup
- `POST /api/standup/resume` - Resume a standup workflow

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines

- Follow the existing code style
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/your-repo/issues) page
2. Create a new issue with detailed information
3. Contact the maintainers

## 🙏 Acknowledgments

- [Slack API](https://api.slack.com/) for platform integration
- [OpenAI](https://openai.com/) for AI capabilities
- [LangGraph](https://github.com/langchain-ai/langgraph) for workflow orchestration
- [Next.js](https://nextjs.org/) for the frontend framework
- [Tailwind CSS](https://tailwindcss.com/) for styling

---

**Made with ❤️ for better team communication**
