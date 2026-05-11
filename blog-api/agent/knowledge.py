"""
Static knowledge base about Testimony Adekoya.
Injected into every conversation — primary anti-hallucination layer.
All facts here are sourced from the portfolio, bio.json, and posts.json.
"""

TESTIMONY_FACTS = """
# Testimony Adekoya — Complete Knowledge Base

## Identity
- **Full name:** Testimony Adekoya
- **Role:** Applied ML Engineer & Researcher
- **Location:** Lagos, Nigeria
- **Email:** testimonyadekoya.02@gmail.com
- **Portfolio:** https://dev-tyta.github.io
- **GitHub:** https://github.com/dev-tyta (username: dev-tyta)
- **LinkedIn:** https://www.linkedin.com/in/testimony-adekoya/
- **X / Twitter:** https://x.com/_testys_ (handle: @_testys_)
- **IEEE Collabratec:** https://ieee-collabratec.ieee.org/app/p/testimonyadekoya

## Summary
Applied ML Engineer with 4+ years of experience building end-to-end production ML systems — from data ingestion and model training to containerised deployment and monitoring on AWS, GCP, and Azure. Independent researcher investigating cultural bias in generative vision models and accessible medical AI.

## Current Roles (as of May 2026)

### DataBacked Africa — Applied ML Engineer (Aug 2025 – Present, Lagos)
Leading architecture of **Intellign** — a decision-intelligence platform where operators describe allocation goals in natural language and a genetic algorithm engine processes 500+ resources against 750+ targets under competing constraints in minutes, streaming real-time progress via SSE. First major deployment: assigned medical graduates to healthcare facilities, compressing a months-long manual process to minutes.
Stack: FastAPI, Genetic Algorithms, SSE, MLOps, Python

### Obscura Finance — Backend Engineer (2025 – Present, Remote)
Backend infrastructure for a crypto copy-trading platform built on cryptographic trust. Traders prove performance without exposing strategies. Work: deployment pipelines, observability stacks, incident response, privacy-preserving verification layer built on Nillion and Horizen.
Stack: DevOps, Blockchain, Privacy Tech, Monitoring, Python

## Past Experience

### Synthik Labs — ML Engineer (Oct–Dec 2025, Remote)
Built multi-modal synthetic data generation pipeline: tabular (ARGN neural nets + parallel LLM inference), text, image. Parallelised LLM inference with schema enforcement, fuzzy deduplication (RapidFuzz), multi-format export (JSON/CSV/Parquet/Arrow/Excel). Filecoin provenance tracking for every dataset.
Stack: PyTorch, FastAPI, Celery, Redis, LLMs, Filecoin

### TAO AI — ML Engineer Intern (May–Oct 2024, Lagos)
Adapted TinyLLaMA for African agricultural contexts on AWS SageMaker. Knowledge distillation for edge deployment. Shipped: production chatbot and credit scoring system for resource-constrained hardware.
Stack: TinyLLaMA, AWS SageMaker, Langchain, Docker, Knowledge Distillation

### Rediones — ML Engineer Contract (May 2023–Sep 2024, Remote)
Built multimodal topic-generation model using CLIP + HuggingFace LLMs to extract content themes from video/audio streams. TTS model with voice cloning for personalised audio. Deployed to GCP via FastAPI.
Stack: CLIP, TTS/Voice Cloning, GCP, HuggingFace, FastAPI

### Zummit Infolabs — Junior Data Scientist Intern (Aug–Nov 2021, Remote)
First professional ML role. Built real-time object detection pipelines for queue wait-time prediction and customer flow optimisation.
Stack: TensorFlow, OpenCV, Object Detection

## Research & Publications

### AfriVTON-Bench (Submitted — Deep Learning Indaba 2026, Under Review)
With Shiloh Oni. Benchmark exposing distribution-shift failures in VTON systems on African textiles.
- 111 African garment images, 16 categories, 7 countries (Nigeria, Ghana, Senegal, Ethiopia, Kenya, South Africa, Morocco)
- 1,012 person-garment evaluation pairs
- Models: FASHN-VTON (g/p ratio 3.63×) vs LEFFA (4.27×)
- 3 failure modes: pattern dissolution, drape collapse, tonal drift
- African garments: 9.4–9.6 percentage points lower gSSIM than Western controls
Paper: https://dev-tyta.github.io/projects/afrivton.html

### MMIBC: Explainable Multimodal Vision Transformer for Breast Cancer Diagnosis (Submitted — MIWAI 2026)
Parallel pretrained ViT backbones for mammography + ultrasonography → feature-level fusion → MLP classifier + Grad-CAM XAI.
- 84% overall classification accuracy (VinDr-Mammo + BUSI datasets)
- Programmatic pairing strategy for unpaired multimodal training
- Best Poster Award — DSN AI+ Bootcamp 2025
Paper: https://dev-tyta.github.io/projects/mmibc.html

## Key Projects

### FAUE (Side project — Pre-build, May 2026)
Fashion intelligence platform for African fashion consumers. Core loop: Style DNA Quiz → personalised cross-brand RTW + bespoke styling recommendations → Shop link or WhatsApp share to tailor. Designed for Nigerian professional who navigates Owambe dress codes, Aso-Ebi, bespoke fabric styling.

### Intellign (Production — DataBacked Africa)
Decision-intelligence platform. Natural language goal description → genetic algorithm optimisation → real-time SSE streaming → human-in-the-loop review. First deployment: medical graduate placement.

### SnapFeast AI
Meal ordering platform with CNN-based facial recognition login (90% accuracy), collaborative filtering recommendations, PostgreSQL order management. FastAPI backend on HuggingFace Spaces.
GitHub: https://github.com/dev-tyta/SnapFeast-AI | Docs: https://testys-snapfeast-ai.hf.space/docs

### Thery AI
Telegram-deployed LLM virtual therapist using RAG, real-time emotion detection, adaptive therapeutic responses, mood-based music recommendations, Redis-backed stateful conversation history.
GitHub: https://github.com/dev-tyta/thery.ai | Telegram: https://t.me/TheryAIBot

### Verifacts
AI-powered fact-checking platform. NLP evidence retrieval → claim classification → verdict (verified/debunked/mixture). Chrome extension + mobile app. Live API: https://verifacts-backend-production.up.railway.app
GitHub: https://github.com/verifacts

### AfriVTON-Bench
See Research section above. GitHub: https://github.com/dev-tyta

### MMIBC
See Research section above. GitHub: https://github.com/dev-tyta/MMIBC

## Technical Skills
**Languages:** Python, C++, SQL
**ML Frameworks:** PyTorch, TensorFlow, Scikit-learn, Keras, OpenCV, HuggingFace Transformers & Diffusers, Pandas, NumPy
**ML Domains:** Computer Vision, NLP, LLM Fine-tuning, RAG, Multimodal ML, Generative Models, Memetic/Genetic Algorithms, Recommender Systems
**MLOps & Infrastructure:** Docker, FastAPI, Celery, Redis, Langchain, CI/CD, Git, HuggingFace Spaces, LangSmith, Prometheus
**Cloud:** AWS SageMaker, AWS EC2/S3, GCP, Azure
**Data & Storage:** PostgreSQL, Pandas, PyArrow, Parquet, Filecoin

## Community & Conferences
- **Deep Learning Indaba 2025** (Kigali, Rwanda) — Participant & Travel Organizing Committee Member
- **African Computer Vision Summer School 2024** (Nairobi, Kenya)
- **Deep Learning Indaba 2023** (Accra, Ghana) — Participant (crowdfunding campaign to attend)
- **DSN AI+ Bootcamp & Hackathon 2025** (Lagos) — Best Poster Award for MMIBC
- **DSN FUNAAB Chapter Lead (Jun 2023–Oct 2025)** — Led 100+ member AI community at Federal University of Agriculture Abeokuta, weekly ML workshops, mentoring

## Currently (May 2026)
- **Building:** FAUE (fashion intelligence for African style), Intellign at DataBacked Africa
- **Researching:** AfriVTON-Bench (under DLI 2026 review)
- **Reading:** Designing Machine Learning Systems (Chip Huyen), The Alignment Problem (Brian Christian), The Mom Test (Rob Fitzpatrick)
- **Open to:** Full-time ML engineering roles, research collaborations, speaking opportunities
- **Now page:** https://dev-tyta.github.io/now.html
"""

# Concise version for injection into compact contexts
TESTIMONY_BRIEF = """
Testimony Adekoya — Applied ML Engineer & Researcher, Lagos, Nigeria.
4+ years building production ML systems. Current: DataBacked Africa (ML Engineer, building Intellign), Obscura Finance (Backend Engineer).
Research: AfriVTON-Bench (DLI 2026) benchmarks VTON on African textiles; MMIBC (MIWAI 2026, Best Poster DSN AI+ 2025) multimodal breast cancer diagnosis.
Side project: FAUE (African fashion intelligence). Key stack: PyTorch, FastAPI, Celery, Redis, LangChain, HuggingFace.
Contact: testimonyadekoya.02@gmail.com | GitHub: dev-tyta | LinkedIn: testimony-adekoya | Twitter: @_testys_
"""
