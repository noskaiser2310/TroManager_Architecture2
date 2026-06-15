# 08. Data Flow & Diagrams

## 1. End-to-End Request Flow

```mermaid
sequenceDiagram
    autonumber
    participant U as User (Zalo)
    participant W as Webhook
    participant G as Gateway
    participant R as Router
    participant S1 as System 1
    participant S2 as System 2
    participant UM as User Modeling
    participant TR as Tool Registry
    participant DB as PostgreSQL
    participant Ext as External APIs

    U->>W: Gửi tin nhắn "Phòng tôi giá bao nhiêu?"
    W->>G: Forward message
    G->>R: classify(query, source)
    R-->>G: {target: system1, confidence: 0.9}
    G->>S1: forward(query)
    S1->>UM: get_profile(tenant_id)
    UM-->>S1: profile
    S1->>DB: cache_lookup(embedding)
    DB-->>S1: miss
    S1->>DB: RAG retrieve
    DB-->>S1: contexts
    S1->>S1: LLM generate (Flash)
    S1->>DB: save_to_cache
    S1-->>G: response
    G-->>U: Gửi reply Zalo
```

## 2. Complex Request Flow (System 2)

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant G as Gateway
    participant S2 as System 2
    participant UM as User Modeling
    participant TR as Tools
    participant DB as DB
    participant Z as Zalo

    U->>G: "Điều hòa phòng tôi bị hỏng, báo giúp tôi"
    G->>G: LLM Router phân loại Intent "maintenance_request" → System 2
    G->>S2: forward
    S2->>UM: build_context(tenant_id, query)
    UM-->>S2: profile + behavior + memories
    S2->>S2: Intent: maintenance_request
    S2->>TR: load_tools(["knowledge", "automation"])
    TR-->>S2: [get_room_info, create_ticket, send_zalo]
    
    Note over S2: ReAct Loop
    
    S2->>S2: Thought: "Cần lấy thông tin phòng trước"
    S2->>TR: get_room_info(tenant_id)
    TR->>DB: Query
    DB-->>TR: Room data
    TR-->>S2: {room_id: 205, ...}
    S2->>S2: Thought: "Tạo ticket maintenance"
    S2->>TR: create_ticket(tenant_id, issue, priority)
    TR->>DB: INSERT
    DB-->>TR: ticket_id
    TR-->>S2: {ticket_id: TKT-1234}
    S2->>S2: Thought: "Gửi xác nhận cho tenant"
    S2->>TR: send_zalo(tenant_id, message)
    TR->>Z: API call
    Z-->>TR: success
    TR-->>S2: {sent: true}
    S2->>S2: Final Answer: "Đã tạo ticket TKT-1234..."
    S2->>UM: log_behavior(auto_maintenance_ticket)
    S2-->>G: response
    G-->>U: "Đã tạo yêu cầu sửa chữa, kỹ thuật sẽ liên hệ anh trong 24h"
```

## 3. Background Event Flow (Cron)

```mermaid
sequenceDiagram
    autonumber
    participant S as Scheduler
    participant D as Detector
    participant E as EventDispatcher
    participant S2 as System 2
    participant UM as User Modeling
    participant T as Tools
    participant Z as Zalo
    participant DB as DB

    S->>D: 9:00 AM - check_invoice_overdue
    D->>DB: SELECT overdue invoices
    DB-->>D: [invoice_id: 456, tenant_id: 123, days_overdue: 3]
    D->>E: dispatch(event_type, tenant_id, data)
    E->>UM: build_context(tenant_id, instruction)
    UM-->>E: {profile, behavior, memories}
    E->>E: anti_spam_check() → OK
    E->>S2: run(instruction, context, tools=[send_zalo])
    S2->>S2: Generate personalized message
    S2->>T: send_zalo(tenant_id, message)
    T->>Z: Send
    Z-->>T: success
    T-->>S2: ok
    S2->>UM: log_behavior(auto_invoice_reminder)
    E-->>D: done
```

## 4. Component Architecture

```mermaid
graph TB
    subgraph "External"
        ZALO[Zalo OA]
        SMS[SMS Gateway]
        LLMP[gemini-3.1-flash-lite<br/>bản pro]
        LLMF[gemma-4-31b-it<br/>bản flash]
        EMB[Embedding API<br/>gemini-embedding-2]
    end
    
    subgraph "Application Layer"
        API[FastAPI Webhook]
        CRON[APScheduler]
    end
    
    subgraph "Routing"
        GW[Router Gateway]
    end
    
    subgraph "Processing"
        S1[System 1<br/>Fast Layer]
        S2[System 2<br/>ReAct Agent]
    end
    
    subgraph "Intelligence"
        UML[User Modeling<br/>Layer]
        TR[Tool Registry]
    end
    
    subgraph "Storage"
        PG[(PostgreSQL<br/>+ pgvector)]
        KB[(Knowledge Base<br/>LlamaIndex)]
    end
    
    ZALO --> API
    API --> GW
    CRON --> S2
    GW --> S1
    GW --> S2
    S1 --> KB
    S1 --> LLMF
    S2 --> TR
    S2 --> LLMP
    S2 --> UML
    S1 --> UML
    UML --> PG
    TR --> PG
    TR --> ZALO
    TR --> SMS
    KB --> PG
```

## 5. Database ERD

```mermaid
erDiagram
    USER_PROFILES ||--o{ BEHAVIOR_LOGS : "has many"
    USER_PROFILES ||--o{ USER_EMBEDDINGS : "has many"
    USER_PROFILES ||--o{ INVOICES : "has many"
    USER_PROFILES ||--o{ CONTRACTS : "has one"
    USER_PROFILES ||--o{ MAINTENANCE_TICKETS : "has many"
    INVOICES ||--o{ PAYMENTS : "paid by"
    CONTRACTS ||--o{ PAYMENTS : "generates"
    ROOMS ||--o{ INVOICES : "billed to"
    ROOMS ||--o{ CONTRACTS : "rented as"
    
    USER_PROFILES {
        int tenant_id PK
        string full_name
        string phone_number UK
        int room_id FK
        date lease_start
        date lease_end
        string communication_preference
        string tone_preference
        timestamp created_at
    }
    
    BEHAVIOR_LOGS {
        int log_id PK
        int tenant_id FK
        string action_type
        text description
        timestamp timestamp
    }
    
    USER_EMBEDDINGS {
        int memory_id PK
        int tenant_id FK
        text memory_text
        vector embedding
        timestamp created_at
    }
    
    SEMANTIC_CACHE {
        int cache_id PK
        text query_text
        vector query_embedding
        text response_text
        timestamp last_accessed
    }
    
    INVOICES {
        int invoice_id PK
        int tenant_id FK
        int room_id FK
        decimal amount
        date due_date
        string status
    }
    
    ROOMS {
        int room_id PK
        decimal area
        int floor
        decimal monthly_rent
        string status
    }
    
    CONTRACTS {
        int contract_id PK
        int tenant_id FK
        int room_id FK
        date start_date
        date end_date
        string status
    }
```

## 6. Deployment Architecture

```mermaid
graph TB
    subgraph "Client"
        U[Zalo App<br/>SMS]
    end
    
    subgraph "Edge"
        LB[Load Balancer<br/>Nginx]
    end
    
    subgraph "App Servers"
        A1[App Server 1]
        A2[App Server 2]
        A3[App Server N]
    end
    
    subgraph "Background Workers"
        W1[Cron Worker 1]
        W2[Cron Worker 2]
    end
    
    subgraph "Data Layer"
        PG_PRIMARY[(PostgreSQL<br/>Primary)]
        PG_REPLICA[(PostgreSQL<br/>Read Replica)]
        REDIS[(Redis<br/>Session Cache)]
    end
    
    subgraph "External APIs"
        GEMINI[Google Gemini API]
        ZALO_API[Zalo OA API]
        GEMINI_EMB[Gemini Embedding API<br/>gemini-embedding-2]
    end
    
    U --> LB
    LB --> A1
    LB --> A2
    LB --> A3
    A1 --> PG_PRIMARY
    A2 --> PG_PRIMARY
    A3 --> PG_PRIMARY
    A1 --> REDIS
    A2 --> REDIS
    A3 --> REDIS
    PG_PRIMARY -.replicate.-> PG_REPLICA
    A1 --> PG_REPLICA
    A2 --> PG_REPLICA
    A3 --> PG_REPLICA
    
    W1 --> PG_PRIMARY
    W2 --> PG_PRIMARY
    W1 --> REDIS
    
    A1 --> GEMINI
    A1 --> ZALO_API
    A1 --> GEMINI_EMB
```

## 7. State Machine - ReAct Loop

```mermaid
stateDiagram-v2
    [*] --> ContextBuild
    ContextBuild --> Thought1: Inject profile, behavior, memories
    Thought1 --> Action1: Need tool?
    Thought1 --> FinalAnswer: Have enough info
    Action1 --> Observation1: Tool executed
    Observation1 --> Thought2: Continue reasoning
    Thought2 --> Action2: Need another tool?
    Thought2 --> FinalAnswer: Done
    Action2 --> Observation2: Tool executed
    Observation2 --> Thought3: Continue
    Thought3 --> Action3: Need tool?
    Thought3 --> FinalAnswer: Done
    Action3 --> Observation3
    Observation3 --> Thought4
    Thought4 --> FinalAnswer: Done
    Thought4 --> LoopBreaker: Max iterations
    LoopBreaker --> FallbackMessage
    FinalAnswer --> [*]
    FallbackMessage --> [*]
```

## 8. Performance Characteristics

| Operation | Latency P50 | Latency P99 |
|-----------|-------------|-------------|
| Gateway routing | 10ms | 50ms |
| Embedding generation | 80ms | 200ms |
| Cache lookup (pgvector) | 15ms | 50ms |
| System 1 (cache hit) | 150ms | 300ms |
| System 1 (cache miss + RAG) | 1.5s | 3s |
| System 2 (1 tool call) | 4s | 8s |
| System 2 (2-3 tool calls) | 8s | 15s |
| ReAct fallback | 12s | 18s |
| Zalo send | 200ms | 500ms |
| Behavior log write | 5ms | 20ms |

## 9. Tham Khảo Diagrams

- `../diagrams/01_architecture_overview.mmd` - Overview
- `../diagrams/02_router_logic.mmd` - Router decision
- `../diagrams/03_react_loop.mmd` - ReAct detail
- `../diagrams/04_proactive_event.mmd` - Cron event
