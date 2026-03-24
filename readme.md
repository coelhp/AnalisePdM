# SKF Observer Phoenix — Dashboard de Monitoramento

Dashboard interativo em Streamlit para consulta e visualização de dados do **SKF Observer Phoenix API v2.0**. Permite navegar pela hierarquia de ativos, explorar pontos de medição, plotar tendências históricas e analisar espectros de vibração em tempo real.

---

## Funcionalidades

- **Autenticação** via Bearer Token na API do Observer Phoenix
- **Listagem de Assets** (máquinas) com status, descrição e path hierárquico
- **Listagem de Points** por máquina com tipo e unidade de medição
- **Gráfico de Tendência** interativo com:
  - Seletor de canal de medição (multi-canal)
  - Bandas estatísticas ±1σ
  - Linhas de alerta (μ+2σ) e alarme (μ+3σ)
  - Eixo secundário de velocidade (RPM) quando disponível
  - Exportação de dados brutos em CSV
- **Gráfico de Espectro de Vibração** interativo com:
  - Marcadores automáticos dos top 10 picos
  - Linhas harmônicas de rotação (1X a 5X) quando velocidade está disponível
  - Seletor de canal/direção (X, Y, Z etc.)
  - Range slider para zoom na faixa de frequência
  - Exportação de picos e espectro completo em CSV
- **Tema industrial dark** com fontes Rajdhani, Share Tech Mono e Exo 2

---

## Requisitos

- Python 3.9+
- SKF Observer Phoenix rodando localmente (padrão: `http://127.0.0.1:14050`)

---

## Instalação

```bash
pip install -r requirements.txt
```

Conteúdo do `requirements.txt`:

```
streamlit>=1.32.0
requests>=2.31.0
pandas>=2.1.0
plotly>=5.18.0
numpy>=1.26.0
```

---

## Execução

```bash
streamlit run skf_observer_app.py
```

Acesse o dashboard em `http://localhost:8501`.

---

## Uso

### 1. Conectar

Na barra lateral, informe:

- **Servidor** — URL base do Observer Phoenix (ex: `http://127.0.0.1:14050`)
- **Usuário** e **Senha** — credenciais da API (padrão: `admin` / `admin`)

Clique em **🔌 Conectar**. O app autentica e carrega a lista de assets automaticamente.

### 2. Selecionar Asset

A tabela exibe todos os ativos cadastrados com ID, nome, descrição, path e status. Selecione um asset no menu e clique em **⟶ Carregar Points**.

### 3. Selecionar Point e carregar dados

Com a lista de points carregada, selecione o ponto de medição desejado. Em seguida use:

- **📈 Carregar Tendência** — busca o histórico de leituras no período configurado na sidebar
- **〜 Carregar Espectro** — busca a última medição dinâmica (espectro FFT)

Os dois podem ser carregados de forma independente para o mesmo ponto.

### 4. Filtros (sidebar)

| Filtro | Descrição |
|--------|-----------|
| **De / Até** | Intervalo de datas para a tendência |
| **Máx. leituras** | Limite de pontos retornados (10–5000) |

---

## Endpoints Utilizados

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/token` | Autenticação (grant_type=password) |
| `GET` | `/v2/assets` | Lista de máquinas |
| `GET` | `/v2/points` | Points de um asset |
| `GET` | `/v2/trend` | Leituras históricas de tendência |
| `GET` | `/v1/points/{pointId}/dynamicMeasurements` | Espectro de vibração (última medição) |

---

## Estrutura dos Dados

### Tendência (`/v2/trend`)

Cada leitura retornada segue o formato:

```json
{
  "ReadingTimeUTC": "2026-03-10T18:45:15.353",
  "Speed": 1480.0,
  "SpeedUnits": "RPM",
  "Process": 36.0,
  "Measurements": [
    {
      "Channel": 1,
      "Direction": "X",
      "ChannelName": "Overall",
      "Level": 4.52,
      "Units": "mm/s",
      "BOV": 0.0
    }
  ]
}
```

O parser `parse_trend()` suporta também o formato legado com campos planos (`timestamp`, `value.value`).

### Espectro (`/v1/points/{id}/dynamicMeasurements`)

```json
{
  "SampleRate": 5120.0,
  "Samples": 8192,
  "EU": "m/s^2E",
  "StartFrequency": 0.0,
  "EndFrequency": 2000.0,
  "Speed": 1480.0,
  "SpeedUnits": "RPM",
  "Measurements": [
    {
      "MeasurementType": 2,
      "Direction": 0,
      "Values": [0.001, 0.003, ...]
    }
  ]
}
```

O eixo de frequência é calculado por interpolação linear entre `StartFrequency` e `EndFrequency` com `len(Values)` pontos.

---

## Estrutura do Projeto

```
skf_observer_app.py   # Aplicação principal (único arquivo)
requirements.txt      # Dependências Python
README.md             # Este arquivo
```

---

## Paleta de Cores (Tema Industrial)

| Variável | Hex | Uso |
|----------|-----|-----|
| `--bg-base` | `#090c10` | Fundo principal |
| `--accent` | `#00d9ff` | Destaque / dados primários |
| `--warn` | `#f0a500` | Alerta (μ+2σ) |
| `--danger` | `#ff4757` | Alarme (μ+3σ) |
| `--ok` | `#2ed573` | Normal / média |
| `--purple` | `#a855f7` | Harmônicas / velocidade |

---

## Observações

- O endpoint de espectro retorna a **última medição dinâmica** disponível para o ponto; não há filtro por data.
- Pontos do tipo temperatura ou processo podem não ter medições dinâmicas — neste caso o botão de espectro exibirá um aviso de ponto não disponível (HTTP 404).
- A aplicação não armazena credenciais — o token é mantido apenas em `st.session_state` durante a sessão ativa.
