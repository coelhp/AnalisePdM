# SKF Observer Phoenix — Dashboard de Monitoramento

Dashboard interativo em Streamlit para consulta, análise e visualização de dados do **SKF Observer Phoenix API**. Cobre desde tendências de medição individuais até a topologia completa da rede mesh de sensores IMx-1.

---

## Sumário

- [Funcionalidades](#funcionalidades)
- [Requisitos](#requisitos)
- [Instalação e Execução](#instalação-e-execução)
- [Uso](#uso)
- [Abas do Dashboard](#abas-do-dashboard)
- [Endpoints Utilizados](#endpoints-utilizados)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Paleta de Cores (LDC Brand)](#paleta-de-cores-ldc-brand)
- [Unidades Configuradas](#unidades-configuradas)
- [Observações Técnicas](#observações-técnicas)

---

## Funcionalidades

- **Autenticação** via Bearer Token com renovação automática a cada 18 minutos
- **Seletor de unidade** na sidebar — troca de servidor com um clique, limpando estado automaticamente
- **4 abas independentes** cobrindo monitoramento em tempo real, comissionamento, frota e rede mesh
- **Tema visual LDC Brand** aplicado em todo o dashboard (CSS + Plotly)

---

## Requisitos

- Python 3.9+
- Acesso à API SKF Observer Phoenix (autenticação por usuário/senha)

---

## Instalação e Execução

```bash
pip install -r requirements.txt
streamlit run skf_observer_app.py
```

Acesse em `http://localhost:8501`.

---

## Uso

### 1. Selecionar Unidade

Na barra lateral, clique no botão da unidade desejada. A URL do servidor é montada automaticamente. Ao trocar de unidade, todos os dados em cache são limpos.

### 2. Informar Credenciais

Preencha **Usuário** e **Senha** e clique em **🔌 Conectar**. O token é obtido e os assets carregados automaticamente.

### 3. Navegar pelas Abas

Cada aba é independente — explore na ordem que preferir.

---

## Abas do Dashboard

### 📈 Aba 1 — Monitor de Pontos

Navegação hierárquica pela planta: Assets → Points → Dados.

| Funcionalidade | Descrição |
|---|---|
| Tabela de Assets | ID, nome, descrição, path e badge de status |
| Tabela de Points | ID, nome, tipo e unidade de medição |
| Gráfico de Tendência | Linha interativa com banda ±1σ, linhas de alerta (μ+2σ) e alarme (μ+3σ) |
| Seletor de canal | Múltiplos canais por ponto (Ch1 Overall [X] etc.) |
| Eixo secundário | Velocidade (RPM) quando disponível |
| Gráfico de Espectro FFT | Linha de espectro, top 10 picos, harmônicas de rotação (1X–5X) |
| Exportação | CSV de tendência e de espectro (picos e completo) |

**Filtros de tendência (sidebar):** período De/Até e máximo de leituras.

---

### 🔬 Aba 2 — IMx-1 Comissionamento

Varredura completa da planta para identificar a data real de comissionamento de cada sensor IMx-1.

**Fluxo de coleta:**

```
GET /v2/assets
  └── GET /v1/machines/{id}/points          (filtra NodeTypes 11101–11104)
       └── Agrupa por IDNode (sensor físico)
            └── GET /v1/points/{id}/trendMeasurements  (1ª leitura ≥ 01/05/2024)
                 └── GET /v1/nextgensensor              (ClearedDate + bateria)
```

**Regra de data de comissionamento:**

| Condição | Data usada | Fonte |
|---|---|---|
| `ClearedDate` ausente ou ano ≤ 1940 (sentinela) | 1ª leitura de tendência | `"1ª Leitura Tendência"` |
| `ClearedDate` válido (ano > 1940) | ClearedDate | `"ClearedDate (sensor)"` |

**Colunas do DataFrame de saída:**

`HardwareID` · `IDNode` · `MachineID` · `MachineName` · `BatteryLevel` · `SystemCreatedDate` · `DataPrimeiraLeitura` · `DataClearedSensor` · `ProvavelDataComissionamento` · `FonteComissionamento` · `DiasDeUso` · `TaxaConsumoBateria`

**Gráficos:**
- Linha do tempo de comissionamento por mês (barras + acumulado)
- Scatter Bateria × Dias em Campo com regressão linear e zonas de alerta
- Ranking horizontal de taxa de consumo de bateria (top 25)

---

### 🛰 Aba 3 — Fleet Monitoring

Visão completa de conectividade e saúde de toda a frota de hardware.

**Endpoints consumidos:**

| Endpoint | Dados coletados |
|---|---|
| `GET /v1/gateways` | Status online/offline, `statusLastUpdated` |
| `GET /v1/nextgensensor` | `ConnectionState`, `BatteryLevel`, `DiagnosticCode` |
| `GET /v1/device` | `synchronizationstatus`, `lastupdate` |
| `GET /v1/systemcheck` | Itens com falha e `DateDataReceived` |

**Estados de conexão OPC UA (`ConnectionState`):**

| Código | Significado | Alerta |
|---|---|---|
| `0` | Desconectado / Não Comissionado | 🔴 Crítico |
| `1` | Conectado | ✅ Normal |
| `2` | Sem Medição | ⚠ Aviso |
| `3` | Conectado — Sem Medição | ⚠ Aviso |

**Status de sincronização (`synchronizationstatus`):**

| Código | Significado |
|---|---|
| `0` | Não Sincronizado |
| `1` | Sincronizado |
| `2` | Pendente |
| `100` | Falha |

**Códigos de autodiagnóstico (bitwise):**

| Bit | Significado |
|---|---|
| `1` | Bateria Baixa |
| `512` | Instabilidade de Rede (mesh) |

**3 níveis de visualização:**
- **Nível 1:** KPI cards de frota + alertas automáticos multinível
- **Nível 2:** Pizza de gateways, barras de ConnectionState, scatter Bateria × Dias offline
- **Nível 3:** Sub-tabs por tipo (sensores / dispositivos cabeados / system check) com tabelas filtráveis e exportação CSV

---

### 🕸 Aba 4 — Rede Mesh

Reconstrói e visualiza a topologia da rede mesh IMx-1 como grafo hierárquico interativo.

**Endpoints:**

| Endpoint | Uso |
|---|---|
| `GET /v1/gateways` | Nós raiz (pentágonos) |
| `GET /v1/nextgensensor` | Sensores com `IDMeshParent` e `ParentLinkMetric` |

**Lógica do grafo:**
- Cada `IDNode` é um nó; aresta de filho → `IDMeshParent`
- Layout hierárquico top-down com raízes nos gateways
- BFS para calcular **hops** (saltos) de cada sensor até o gateway mais próximo
- Classificação automática: **Mesh** (tem filhos) vs **Leaf** (extremidade)

**Visual:**

| Elemento | Forma | Tamanho |
|---|---|---|
| Gateway | Pentágono | 28 px |
| Sensor Mesh | Círculo | 18 px |
| Sensor Leaf | Círculo | 12 px |

**Qualidade do link (`ParentLinkMetric`):**

| Faixa | Cor | Estilo |
|---|---|---|
| ≤ 1.7 | Verde `#4E9D2D` | Sólido espesso |
| 1.7 – 2.5 | Âmbar `#BA944B` | Sólido |
| > 2.5 | Laranja `#F06A22` | Pontilhado |

**Filtros:** LocationTag e nível de alerta. Nós sem rota ao gateway aparecem como órfãos à direita.

**Gráficos analíticos:**
- Distribuição de hops por número de sensores
- Histograma de `ParentLinkMetric` com limiares marcados
- Tabela detalhada exportável

> **Dependência extra:** requer `networkx>=3.2` (`pip install networkx`).

---

## Endpoints Utilizados

| Método | Endpoint | Aba |
|---|---|---|
| `POST` | `/token` | Todas |
| `GET` | `/v2/assets` | 1, 2 |
| `GET` | `/v2/points` | 1 |
| `GET` | `/v1/machines/{id}/points` | 2 |
| `GET` | `/v1/points/{id}/trendMeasurements` | 2 |
| `GET` | `/v2/trend` | 1 |
| `GET` | `/v1/points/{id}/dynamicMeasurements` | 1 |
| `GET` | `/v1/nextgensensor` | 2, 3, 4 |
| `GET` | `/v1/gateways` | 3, 4 |
| `GET` | `/v1/device` | 3 |
| `GET` | `/v1/systemcheck` | 3 |

---

## Estrutura do Projeto

```
skf_observer_app.py   # Aplicação principal (~4 100 linhas)
requirements.txt      # Dependências Python
README.md             # Este arquivo
```

---

## Paleta de Cores (LDC Brand)

| Variável CSS | Hex | Uso |
|---|---|---|
| `--bg-base` | `#0e1820` | Fundo principal |
| `--bg-card` | `#162130` | Cards e painéis |
| `--accent-solid` | `#32556E` | Blue — bordas, botões |
| `--accent` | `#A7C5E2` | Blue claro — valores, texto de destaque |
| `--accent-deep` | `#007CAA` | Azul vivo — hover |
| `--ok` | `#4E9D2D` | Green — normal / sucesso |
| `--warn` | `#BA944B` | Âmbar — aviso |
| `--danger` | `#F06A22` | Laranja — crítico |
| `--teal` | `#379A8D` | Teal — informação / saúde |
| `--purple` | `#5E699E` | Eixo secundário (RPM) |
| `--grey` | `#5C6670` | Grey |
| `--text-mid` | `#98C0B8` | Texto médio / labels |

---

## Unidades precisam ser previamente configuradas

| Unidade | Porta | URL |
|---|---|---|
| xxxxx | 81818 | `http://services.repcenter.skf.com:81818` |
| xxxxx | 81818 | `http://services.repcenter.skf.com:81818` |
| xxxxx | 81818 | `http://services.repcenter.skf.com:81818` |
| xxxxx | 81818 | `http://services.repcenter.skf.com:81818` |
| xxxxx | 81818 | `http://services.repcenter.skf.com:81818` |

Ao trocar de unidade, todo o estado em cache (assets, points, trend, espectro, IMx, fleet, mesh) é limpo automaticamente.

---

## Observações Técnicas

- **Token:** renovado automaticamente após 18 minutos durante varreduras longas (`_ensure_token`)
- **Delay entre chamadas:** 150 ms entre requisições de tendência nas varreduras IMx e Fleet para não sobrecarregar o Monitor Service
- **Sentinela de data:** `ClearedDate` com ano ≤ 1940 é tratado como campo vazio pela API
- **Espectro:** endpoint `/v1/points/{id}/dynamicMeasurements` retorna apenas a última medição dinâmica; não há filtro por data
- **Grafo mesh:** nós sem `IDMeshParent` válido (sem rota até um gateway) aparecem como órfãos no grafo
- **Credenciais:** armazenadas apenas em `st.session_state` durante a sessão; não persistem entre recarregamentos
