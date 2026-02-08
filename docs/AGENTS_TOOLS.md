# 🛠️ Ferramentas por Agente - Dunder Mifflin

Documento completo de ferramentas, dependências e requisitos para cada um dos 50 agentes.

## 📋 Índice por Departamento

- [Agentes Autônomos (7)](#agentes-autônomos)
- [Desenvolvimento (9)](#desenvolvimento)
- [Design & UX (8)](#design--ux)
- [Produto (4)](#produto)
- [Marketing & Growth (7)](#marketing--growth)
- [Gestão de Projetos (3)](#gestão-de-projetos)
- [Operações do Studio (5)](#operações-do-studio)
- [Testes & QA (8)](#testes--qa)

---

## 🤖 Agentes Autônomos

### ⚡ Bolt (Performance)
**Ferramentas:**
- [ ] Lighthouse CLI (`npm install -g lighthouse`)
- [ ] Webpack Bundle Analyzer
- [ ] Chrome DevTools Protocol
- [ ] k6 (load testing)
- [ ] Sitespeed.io

**Instalação:**
```bash
npm install -g lighthouse @sitespeed.io/sitespeed.io
```

---

### 🛡️ Sentinel (Segurança)
**Ferramentas:**
- [ ] GitLeaks (detecta secrets)
- [ ] Semgrep
- [ ] Trivy (vulnerability scanner)
- [ ] OWASP Dependency Check
- [ ] SonarQube CLI

**Instalação:**
```bash
# GitLeaks
docker pull zricethezav/gitleaks

# Semgrep
pip install semgrep

# Trivy
docker pull aquasec/trivy
```

---

### 🧹 Janitor (Limpeza de Código)
**Ferramentas:**
- [ ] depcheck (unused dependencies)
- [ ] unimport (Python)
- [ ] ts-prune (TypeScript)
- [ ] deadcode (Go)

**Instalação:**
```bash
npm install -g depcheck
pip install unimport
npm install -g ts-prune
```

---

### 🔄 Migrator (Migrações)
**Ferramentas:**
- [ ] n (Node version manager)
- [ ] pyenv (Python)
- [ ] rustup
- [ ] codemod (transformações)

---

### 🎯 Optimizer (Otimização)
**Ferramentas:**
- [ ] Black (Python formatter)
- [ ] Prettier
- [ ] ESLint
- [ ] Ruff (Python linter rápido)

---

### ♿ A11y Specialist (Acessibilidade)
**Ferramentas:**
- [ ] axe-core
- [ ] pa11y
- [ ] Lighthouse (a11y audit)
- [ ] WAVE (Web Accessibility Evaluation Tool)

**Instalação:**
```bash
npm install -g pa11y
```

---

### 🌍 i18n Specialist (Internacionalização)
**Ferramentas:**
- [ ] i18next-parser
- [ ] formatjs/cli
- [ ] react-intl
- [ ] RTLCSS (para idiomas RTL)

---

## 💻 Desenvolvimento

### 🐛 Debugger
**Ferramentas:**
- [ ] gdb (C/C++)
- [ ] pdb (Python)
- [ ] node --inspect
- [ ] delve (Go)
- [ ] rr (record & replay debugger)

---

### 🧪 Tester
**Ferramentas:**
- [ ] Jest
- [ ] Cypress
- [ ] Playwright
- [ ] pytest
- [ ] Mocha

**Instalação:**
```bash
npm install -g jest cypress @playwright/test
pip install pytest
```

---

### 🔍 Code Reviewer
**Ferramentas:**
- [ ] GitHub CLI (`gh`)
- [ ] reviewdog
- [ ] Danger JS
- [ ] ESLint
- [ ] SonarLint

**Instalação:**
```bash
# macOS
brew install gh

# Linux
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
```

---

### 🏗️ Architect
**Ferramentas:**
- [ ] Structurizr (diagramas C4)
- [ ] PlantUML
- [ ] Mermaid CLI
- [ ] draw.io CLI

**Instalação:**
```bash
npm install -g @mermaid-js/mermaid-cli
```

---

### 💻 Fullstack Developer
**Ferramentas:**
- [ ] Node.js + npm
- [ ] Python + pip
- [ ] Docker
- [ ] VS Code CLI
- [ ] Postman / curl

---

### 🤖 AI Engineer
**Ferramentas:**
- [ ] Python 3.10+
- [ ] OpenAI SDK
- [ ] LangChain
- [ ] Hugging Face Transformers
- [ ] Ollama (local LLMs)

**Instalação:**
```bash
pip install openai langchain transformers
```

---

### 🗄️ Database Engineer
**Ferramentas:**
- [ ] PostgreSQL CLI (psql)
- [ ] MySQL CLI
- [ ] MongoDB Shell
- [ ] Redis CLI
- [ ] pgAdmin / DBeaver CLI

---

### 🔄 CI/CD Engineer
**Ferramentas:**
- [ ] Docker
- [ ] kubectl
- [ ] Helm
- [ ] Terraform
- [ ] Ansible
- [ ] GitHub Actions CLI

**Instalação:**
```bash
# Docker
curl -fsSL https://get.docker.com | sh

# kubectl
curl -LO "https://dl.k8s/release/$(curl -L -s https://dl.k8s/release/stable.txt)/bin/linux/amd64/kubectl"
```

---

### 🔌 API Designer
**Ferramentas:**
- [ ] Swagger CLI
- [ ] OpenAPI Generator
- [ ] Postman CLI (newman)
- [ ] Insomnia CLI
- [ ] HTTPie

**Instalação:**
```bash
npm install -g @openapitools/openapi-generator-cli newman
pip install httpie
```

---

### ⚡ Rapid Prototyper
**Ferramentas:**
- [ ] Vercel CLI
- [ ] Netlify CLI
- [ ] Create React App / Vite
- [ ] CodeSandbox CLI
- [ ] ngrok

**Instalação:**
```bash
npm install -g vercel netlify-cli ngrok
npm create vite@latest
```

---

## 🎨 Design & UX

### 🎨 UI Designer
**Ferramentas:**
- [ ] Figma CLI
- [ ] Storybook
- [ ] Chromatic
- [ ] Loki (visual regression)

---

### 🔬 UX Researcher
**Ferramentas:**
- [ ] Hotjar CLI
- [ ] Mixpanel
- [ ] Amplitude
- [ ] Hotjar

---

### ✍️ UX Writer
**Ferramentas:**
- [ ] Vale (prose linter)
- [ ] write-good
- [ ] LanguageTool
- [ ] Grammarly API

**Instalação:**
```bash
npm install -g write-good
pip install vale
```

---

### 🎨 Palette (Design System)
**Ferramentas:**
- [ ] Style Dictionary
- [ ] Tailwind CSS
- [ ] Chroma.js
- [ ] ColorThief

---

### 💎 Polish
**Ferramentas:**
- [ ] Lottie CLI
- [ ] GSAP
- [ ] Framer Motion

---

### 🛡️ Brand Guardian
**Ferramentas:**
- [ ] Brandfolder API
- [ ] Frontify API

---

### 📖 Visual Storyteller
**Ferramentas:**
- [ ] FFmpeg
- [ ] ImageMagick
- [ ] Canva API

---

### ✨ Whimsy Injector
**Ferramentas:**
- [ ] canvas-confetti
- [ ] GSAP

---

## 📦 Produto

### 🔬 Researcher
**Ferramentas:**
- [ ] Ahrefs API
- [ ] SEMrush API
- [ ] SimilarWeb API
- [ ] Crunchbase API

---

### 🎯 Feedback Synthesizer
**Ferramentas:**
- [ ] MonkeyLearn
- [ ] Google Natural Language API
- [ ] spaCy

---

### 📊 Sprint Prioritizer
**Ferramentas:**
- [ ] Linear CLI
- [ ] Jira CLI
- [ ] ClickUp API

---

### 🔮 Trend Researcher
**Ferramentas:**
- [ ] Google Trends API
- [ ] BuzzSumo API
- [ ] Reddit API

---

## 📢 Marketing & Growth

### 📝 Content Creator
**Ferramentas:**
- [ ] Buffer API
- [ ] Hootsuite API
- [ ] Sprout Social API

---

### 🚀 Growth Hacker
**Ferramentas:**
- [ ] Google Analytics API
- [ ] Mixpanel
- [ ] Amplitude

---

### 📱 App Store Optimizer
**Ferramentas:**
- [ ] AppTweak API
- [ ] Sensor Tower API

---

---

## 📊 Gestão de Projetos

### 🎬 Studio Producer
**Ferramentas:**
- [ ] Linear
- [ ] Notion API
- [ ] Asana API
- [ ] Monday.com API

---

---

## 🏢 Operações do Studio

### 🔧 Infrastructure Maintainer
**Ferramentas:**
- [ ] Datadog CLI
- [ ] New Relic CLI
- [ ] PagerDuty CLI
- [ ] AWS CLI
- [ ] GCP CLI

**Instalação:**
```bash
# AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# GCP CLI
curl https://sdk.cloud.google.com | bash
```

---

### 💰 Finance Tracker
**Ferramentas:**
- [ ] Stripe CLI
- [ ] QuickBooks API
- [ ] Plaid API

---

### ⚖️ Legal Compliance Checker
**Ferramentas:**
- [ ] OneTrust
- [ ] BigID
- [ ] Cookiebot

---

### 📊 Analytics Specialist
**Ferramentas:**
- [ ] Segment
- [ ] Amplitude
- [ ] Mixpanel
- [ ] Google Analytics 4

---

## 🧪 Testes & QA

### 🎭 Mocker
**Ferramentas:**
- [ ] Faker.js
- [ ] Factory Boy (Python)
- [ ] MockServer

**Instalação:**
```bash
npm install -g @faker-js/faker
pip install factory_boy
```

---

### 🔌 API Tester
**Ferramentas:**
- [ ] Postman / Newman
- [ ] REST Assured
- [ ] Karate DSL
- [ ] Pact (contract testing)

---

### 🚀 Performance Benchmarker
**Ferramentas:**
- [ ] k6
- [ ] Apache Bench (ab)
- [ ] wrk
- [ ] Artillery

**Instalação:**
```bash
# k6
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

---

### 🔬 Tool Evaluator
**Ferramentas:**
- [ ] npm / pip / cargo (package managers)
- [ ] Snyk CLI
- [ ] npm audit

---

### 📊 Test Results Analyzer
**Ferramentas:**
- [ ] Allure
- [ ] ReportPortal
- [ ] SonarQube

---

---

## 🚀 Instalação em Massa (Setup Script)

Crie `setup-tools.sh`:

```bash
#!/bin/bash
# Setup de ferramentas para todos os agentes

echo "Instalando ferramentas globais..."

# Node.js tools
npm install -g lighthouse lighthouse-ci @sitespeed.io/sitespeed.io
npm install -g depcheck ts-prune
npm install -g pa11y @mermaid-js/mermaid-cli
npm install -g jest cypress @playwright/test newman
npm install -g vercel netlify-cli ngrok
npm install -g write-good
npm install -g @faker-js/faker
npm install -g @openapitools/openapi-generator-cli

# Python tools
pip install semgrep unimport black ruff pytest factory_boy
pip install openai langchain transformers
pip install vale
pip install httpie

echo "Instalando CLI tools..."

# Docker (se não instalado)
# kubectl
# AWS CLI
# GCP CLI
# k6

echo "Setup completo!"
```

---

## 📝 Checklist de Instalação

- [ ] Node.js 18+ instalado
- [ ] Python 3.10+ instalado
- [ ] Docker instalado
- [ ] Git instalado
- [ ] GitHub CLI (`gh`) instalado
- [ ] Ferramentas de desenvolvimento instaladas
- [ ] Variáveis de ambiente configuradas (GITHUB_TOKEN, etc.)

---

*Documento gerado em: 08/02/2026*
*Versão: 1.0*
