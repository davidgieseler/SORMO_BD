# Sistema de Otimização de Rotas Multi-Objetivo - Versão Simplificada

## 📋 Visão Geral do Projeto

Sistema de otimização de rotas focado no mercado brasileiro, desenvolvido como versão simplificada para implementação rápida. O projeto utiliza algoritmos de IA para calcular múltiplas rotas otimizadas considerando diferentes critérios (distância, tempo, qualidade das estradas, pedágios, etc.).

### Objetivo
Criar uma aplicação desktop que permita ao usuário selecionar pontos no mapa e receber sugestões de rotas otimizadas baseadas em diferentes critérios, com foco específico nas condições e infraestrutura brasileira.

### Stack Tecnológica
- **Frontend**: Java com JavaFX + FXML (SceneBuilder para design)
- **Backend**: Python 3.10+
- **Comunicação**: REST API (JSON)
- **Cache**: Arquivos JSON locais (incremental)
- **Mapas**: OpenStreetMap com foco em dados brasileiros

---

## 🎯 Funcionalidades Principais

### Frontend (JavaFX)

#### Tela 1: Boas-Vindas
- Nome do aplicativo com logo
- Informações climáticas da localização atual do usuário
- Data e hora atualizadas em tempo real
- Botão "Iniciar" para acessar tela principal
- API usada: OpenWeatherMap (free tier)

#### Tela 2: Seleção de Rotas
- **Painel Superior**: Seleções e ajustes
- **Painel Central**: Mapa interativo
  - Visualização de múltiplas rotas com cores diferentes
  - Controles de zoom e pan
- **Painel Inferior**: 
  - Botão "Pesquisar Rotas"
  - Lista de pontos selecionados com coordenadas
  - Informações das rotas calculadas (distância, tempo, custo)

### Backend (Python)

#### Core de Otimização
- Algoritmo genético multi-objetivo (NSGA-II ou similar simplificado)
- Processamento de múltiplos critérios simultaneamente
- Geração de conjunto Pareto de soluções ótimas

#### Sistema de Cache Inteligente
- Cache incremental em arquivos JSON
- Estrutura hierárquica de cache:
  - `cache/routes/` - Rotas já calculadas
  - `cache/osm/` - Dados do OpenStreetMap
  - `cache/toll/` - Informações de pedágios (ANTT)
  - `cache/weather/` - Dados climáticos
- Hash de requisições para evitar recálculos
- Limpeza automática de cache antigo (opcional)

#### Integração com APIs
- **Routing**: OSRM (Open Source Routing Machine) - auto-hospedado ou instância pública
- **Mapas**: OpenStreetMap Brasil
- **Pedágios**: ANTT Open Data (dados abertos do governo brasileiro)
- **Clima**: OpenWeatherMap API (free tier)
- **Qualidade de Estradas**: Dados do DNIT (Departamento Nacional de Infraestrutura de Transportes)

---

## 🏗️ Arquitetura do Sistema

### Fluxo de Dados

```
┌─────────────────┐
│   JavaFX App    │
│  (Frontend)     │
└────────┬────────┘
         │ HTTP REST
         ↓
┌─────────────────┐
│  Flask/FastAPI  │
│   (Backend)     │
└────────┬────────┘
         │
    ┌────┴────┐
    ↓         ↓
┌─────┐   ┌──────┐
│Cache│   │ APIs │
│JSON │   │ Free │
└─────┘   └──────┘
```

### Comunicação Frontend ↔ Backend

**Endpoint Principal**: `POST /api/optimize-routes`

**Request Body**:
```json
{
  "points": [
    {"lat": -23.5505, "lon": -46.6333, "type": "origin"},
    {"lat": -22.9068, "lon": -43.1729, "type": "destination"},
    {"lat": -23.2237, "lon": -45.9009, "type": "waypoint"}
  ],
  "preferences": {
    "fastest": true,
    "shortest": true,
    "economical": true,
    "comfortable": true
  },
  "vehicle_type": "car"
}
```

**Response**:
```json
{
  "routes": [
    {
      "id": "route_fastest",
      "type": "fastest",
      "color": "#FF0000",
      "distance_km": 435.2,
      "duration_minutes": 360,
      "toll_cost_brl": 87.50,
      "quality_score": 7.5,
      "waypoints": [
        {"lat": -23.5505, "lon": -46.6333},
        {"lat": -23.4000, "lon": -46.5000},
        ...
      ]
    },
    {
      "id": "route_economical",
      "type": "economical",
      "color": "#00FF00",
      "distance_km": 465.8,
      "duration_minutes": 420,
      "toll_cost_brl": 0.00,
      "quality_score": 6.2,
      "waypoints": [...]
    }
  ],
  "cached": false,
  "calculation_time_ms": 1250
}
```

---

## 🗺️ APIs e Fontes de Dados (Foco Brasil)

### 1. Roteamento Base
**OSRM (Open Source Routing Machine)**
- URL pública: `http://router.project-osrm.org/` ou instância própria
- Dados: OpenStreetMap Brasil
- Atualização: Mensal (dados OSM são bem mantidos no Brasil)
- Uso: Cálculo de rotas base, distâncias, tempos

### 2. Dados de Pedágios
**ANTT (Agência Nacional de Transportes Terrestres)**
- API: Dados Abertos ANTT
- URL: `https://dados.antt.gov.br/`
- Formato: JSON/CSV
- Informações: Localização de praças de pedágio, valores por categoria de veículo
- Atualização: Trimestral

### 3. Qualidade das Estradas
**DNIT (Departamento Nacional de Infraestrutura de Transportes)**
- API: Sistema Nacional de Viação
- Dados: Condição de pavimento, classificação de rodovias
- Alternativa: Crowdsourcing via acelerômetro (implementação futura)

### 4. Clima
**OpenWeatherMap**
- Free Tier: 60 chamadas/minuto, 1.000.000 chamadas/mês
- Dados: Temperatura, condições climáticas, previsão
- Uso: Tela de boas-vindas + alertas de rota

### 5. Mapas Visuais
**OpenStreetMap**
- Tiles: `https://tile.openstreetmap.org/{z}/{x}/{y}.png`
- Dados completos para Brasil
- Alternativa: MapBox (free tier com limite)

---

## 🧠 Algoritmo de Otimização

### Abordagem Multi-Objetivo

O sistema utiliza uma versão simplificada de algoritmo genético para gerar múltiplas soluções:

**Objetivos a Minimizar**:
1. **Tempo de viagem** (minutos)
2. **Distância total** (km)
3. **Custo de pedágios** (R$)
4. **Índice de desconforto** (inversão da qualidade da estrada)

**Processo**:
1. Geração de rotas candidatas usando OSRM
2. Avaliação de cada rota nos 4 objetivos
3. Seleção das melhores rotas (Pareto front)
4. Retorno de até 4 rotas otimizadas (uma por tipo)

#### Backend (Python)
1. ✅ Setup Flask/FastAPI básico
2. ✅ Endpoint `/api/optimize-routes`
3. ✅ Integração com OSRM público
4. ✅ Sistema de cache JSON básico
5. ✅ Algoritmo simples de seleção de rotas (sem GA completo inicialmente)

#### Frontend (JavaFX)
1. ✅ Tela de boas-vindas com OpenWeatherMap
2. ✅ Tela principal com mapa (usando JxMaps ou similar)
3. ✅ Seleção de pontos no mapa
4. ✅ Checkboxes de preferências
5. ✅ Requisição HTTP ao backend
6. ✅ Exibição de rotas no mapa

## 🛠️ Dependências Principais

### Backend (Python)
```
fastapi==0.104.1
uvicorn==0.24.0
requests==2.31.0
geopy==2.4.0
polyline==2.0.0
numpy==1.24.3
```

### Frontend (Java)
```
JavaFX 19+
FXML
JxMaps (para mapas interativos)
OU GMapsFX (alternativa)
OkHttp (para requisições HTTP)
Gson (para parsing JSON)
```

---

## 📚 Recursos e Referências

### APIs e Dados
- [OSRM Documentation](http://project-osrm.org/)
- [OpenStreetMap Brasil](https://www.openstreetmap.org/relation/59470)
- [ANTT Dados Abertos](https://dados.antt.gov.br/)
- [OpenWeatherMap API](https://openweathermap.org/api)
- [Mapillary API](https://www.mapillary.com/developer)

### Algoritmos
- [NSGA-II Paper](https://ieeexplore.ieee.org/document/996017)
- [Multi-Objective Routing](https://en.wikipedia.org/wiki/Multi-objective_optimization)

### JavaFX
- [JavaFX Documentation](https://openjfx.io/)
- [SceneBuilder](https://gluonhq.com/products/scene-builder/)
- [JxMaps](https://www.teamdev.com/jxmaps)

---

## ⚠️ Considerações Importantes

1. **APIs Gratuitas**: Respeitar rate limits (implementar retry e backoff)
2. **Cache**: Essencial para não exceder limites das APIs free
