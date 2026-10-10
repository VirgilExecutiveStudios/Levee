[![Levee Marketing Site](https://img.shields.io/badge/Levee-Marketing%20Site-00C9A7?style=for-the-badge&logo=googlechrome&logoColor=white)](https://VirgilExecutiveStudios.github.io/Levee/)

# Levee

Levee is an automated EdTech verification engine designed to verify educational content across websites, forms, pages, and local folders against authoritative internet data sources. It provides real-time grounding, confidence scoring, and human-in-the-loop review to ensure the accuracy and reliability of educational concepts.

## 🚀 Features

- **Automated Verification**: Leverages web search and large language models to verify educational concepts.
- **Human-in-the-Loop**: Flags low-confidence results for expert review.
- **Multi-Source Grounding**: Uses authoritative educational domains (OpenStax, Khan Academy, NCES, etc.).
- **Extensible Architecture**: Supports multiple LLM providers (OpenAI, Anthropic, Google Gemini, Ollama).
- **Persistent Storage**: Stores all verification results with citations and metadata.
- **Flexible Deployment**: Runs as a Dockerized FastAPI service with Chrome extension and web dashboard.

## 🔗 Links

- **Live Demo**: https://VirgilExecutiveStudios.github.io/Levee/
- **Documentation**: https://VirgilExecutiveStudios.github.io/Levee/
- **API Reference**: https://VirgilExecutiveStudios.github.io/Levee/
- **Source Code**: https://github.com/VirgilExecutiveStudios/Levee
- **Official Marketing & Documentation Site**: https://VirgilExecutiveStudios.github.io/Levee/
- [Levee.Github - Automated Sourcing & More](https://VirgilExecutiveStudios.github.io/Levee/)

## 📁 Project Structure

```
Levee/
├── assets/                   # Static assets (logos, images)
│   ├── logo.svg
│   └── .gitkeep
├── apps/                     # Additional web applications
│   ├── installer/            # Installation wizard UI
│   │   └── index.html
│   ├── local-app/            # Local verification tool dashboard
│   │   └── index.html
│   └── marketing/            # Marketing site / documentation landing page
│       └── index.html
├── backend/                  # FastAPI backend service
│   ├── Dockerfile
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── requirements.txt
│   ├── schemas.py
│   └── services/
│       ├── retriever.py      # Tavily web grounding
│       └── verifier.py       # Multi-LLM verification
├── extension/                # Chrome/Edge browser extension (Manifest V3)
│   ├── icons/
│   │   ├── icon16.png
│   │   └── icon128.png
│   ├── manifest.json
│   ├── popup.html
│   └── popup.js
├── web-dashboard/            # Standalone review dashboard
│   ├── app.js
│   ├── index.html
│   └── style.css
├── .dockerignore
├── .gitignore
├── .env.example
├── docker-compose.yml
├── LICENSE
└── README.md
```

## 🛠️ Installation & Setup

### Prerequisites

- Docker and Docker Compose
- API keys for Tavily and at least one LLM provider (OpenAI, Anthropic, etc.)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/VirgilExecutiveStudios/Levee.git
   cd levee
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env to add your API keys:
   # TAVILY_API_KEY=your_tavily_key
   # OPENAI_API_KEY=your_openai_key
   # ANTHROPIC_API_KEY=your_anthropic_key
   # LLM_MODEL=gpt-4o-mini  # or your preferred model
   ```

3. **Start the services**
   ```bash
   docker compose up --build
   ```

4. **Access the system**
   - Backend API: http://localhost:8000
   - Health check: http://localhost:8000/health
   - Load the Chrome extension from the `extension/` folder
   - Open `web-dashboard/index.html` to view the review queue

## 🧪 API Endpoints

- `POST /api/v1/verify-entity` - Trigger verification of an educational concept
- `GET /api/v1/review-queue` - Retrieve items requiring human review
- `POST /api/v1/review-queue/{entity_id}/resolve` - Resolve a review item with human feedback
- `GET /health` - Health check endpoint

## 📦 Docker Composition

The `docker-compose.yml` file defines a single service:
- **backend**: The FastAPI application running on port 8000
  - Persists data to a named volume (`levee_data`)
  - Mounts the backend directory for live code updates during development
  - Restarts unless stopped

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](https://docs.levee.example.com/contributing) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Uses [Tavily](https://tavily.com/) for web search grounding
- Leverages [LiteLLM](https://docs.litellm.ai/) for multi-LLM support
- Icon generated via [HeroPatterns](https://www.heropatterns.com/)

---

*Levee: Verifying Education, One Concept at a Time.*