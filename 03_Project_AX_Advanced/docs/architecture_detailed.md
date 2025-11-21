# Detailed Architecture Diagram

**버전**: 0.2.0  
**최종 업데이트**: 2024-11-20

## System Architecture (v0.2.0)

```mermaid
graph TB
    subgraph "User Interface Layer"
        CLI[CLI Interface<br/>cli.py]
        API[REST API<br/>FastAPI]
        LG[LangGraph Studio<br/>Interactive UI]
    end

    subgraph "LangGraph Platform"
        WF[Workflow Engine<br/>graph.py]
        V[Validate Input Node]
        D[Decide Mode Node]
        E[Execute Analysis Node]
        F[Handle Fallback Node]
    end

    subgraph "DeepAgent Coordinator"
        direction TB
        C[ImpactAnalysisCoordinator]
        P[Planning<br/>_create_plan]
        FS[FileSystem<br/>_verify_file_access]
        SA[SubAgent<br/>_execute_with_subagent]
    end

    subgraph "Analysis Engines"
        direction LR
        SPEED[SpeedAnalyzer<br/>Tree-sitter + NetworkX]
        PREC[PrecisionAnalyzer<br/>LSP/Pyright]
    end

    subgraph "Data Models"
        REQ[AnalysisRequest]
        RES[AnalysisResult]
        DEP[DependencyNode]
    end

    subgraph "Utilities"
        FU[File Utils]
        PR[Prompts]
    end

    CLI --> WF
    API --> WF
    LG --> WF

    WF --> V
    V --> D
    D --> E
    E -->|Success| RES
    E -->|Failure| F
    F --> E

    E --> C
    C --> P
    C --> FS
    C --> SA

    SA -->|SPEED Mode| SPEED
    SA -->|PRECISION Mode| PREC

    SPEED --> RES
    PREC --> RES
    PREC -.->|Failed| F

    REQ --> V
    FS --> FU
    P --> PR

    style CLI fill:#bfdbfe,stroke:#1e3a8a
    style API fill:#bfdbfe,stroke:#1e3a8a
    style LG fill:#bfdbfe,stroke:#1e3a8a
    style C fill:#d1fae5,stroke:#065f46
    style SPEED fill:#fecaca,stroke:#b91c1c
    style PREC fill:#fed7aa,stroke:#7c2d12
    style F fill:#ddd6fe,stroke:#4c1d95
```

## Component Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant LangGraph
    participant Coordinator
    participant SPEED
    participant PRECISION
    participant Human

    User->>LangGraph: Submit Analysis Request
    LangGraph->>LangGraph: Validate Input
    LangGraph->>LangGraph: Decide Mode
    
    alt SPEED Mode Selected
        LangGraph->>Coordinator: Execute SPEED
        Coordinator->>Coordinator: Plan Analysis
        Coordinator->>Coordinator: Verify File Access
        Coordinator->>SPEED: Analyze Code
        SPEED->>SPEED: Parse with Tree-sitter
        SPEED->>SPEED: Build NetworkX Graph
        SPEED->>SPEED: BFS Traversal
        SPEED->>Coordinator: Return Dependencies
        Coordinator->>LangGraph: Return Result
        LangGraph->>User: Display Results
    else PRECISION Mode Selected
        LangGraph->>Coordinator: Execute PRECISION
        Coordinator->>Coordinator: Plan Analysis
        Coordinator->>Coordinator: Verify File Access
        Coordinator->>PRECISION: Analyze Code
        PRECISION->>PRECISION: Check Pyright Availability
        
        alt Pyright Available
            PRECISION->>PRECISION: Run LSP Analysis
            PRECISION->>PRECISION: Parse References
            PRECISION->>Coordinator: Return Dependencies
            Coordinator->>LangGraph: Return Result
            LangGraph->>User: Display Results
        else Pyright Not Available
            PRECISION->>Coordinator: Error + Fallback Suggested
            Coordinator->>LangGraph: Suggest Fallback
            LangGraph->>Human: Request Approval
            
            alt User Approves
                Human->>LangGraph: Approve Fallback
                LangGraph->>Coordinator: Execute SPEED
                Coordinator->>SPEED: Analyze Code
                SPEED->>Coordinator: Return Dependencies
                Coordinator->>LangGraph: Return Result (with fallback note)
                LangGraph->>User: Display Results
            else User Rejects
                Human->>LangGraph: Reject Fallback
                LangGraph->>User: Display Error
            end
        end
    end
```

## Data Flow Diagram

```mermaid
flowchart LR
    A[User Input] --> B{Validate}
    B -->|Valid| C[AnalysisRequest]
    B -->|Invalid| Z[Error Response]
    
    C --> D{Mode?}
    D -->|SPEED| E[SpeedAnalyzer]
    D -->|PRECISION| F[PrecisionAnalyzer]
    
    E --> G[Parse Files<br/>Tree-sitter]
    G --> H[Build Graph<br/>NetworkX]
    H --> I[Find Dependencies<br/>BFS]
    I --> J[Rank by Impact<br/>In-degree]
    
    F --> K{Pyright<br/>Available?}
    K -->|Yes| L[Run LSP Analysis]
    K -->|No| M[Suggest Fallback]
    L --> N[Parse References]
    N --> O[Rank by Frequency]
    
    M --> P{Human<br/>Approves?}
    P -->|Yes| E
    P -->|No| Z
    
    J --> Q[AnalysisResult]
    O --> Q
    Q --> R[User Output]
    
    style A fill:#e0e7ff
    style C fill:#dbeafe
    style E fill:#fecaca
    style F fill:#fed7aa
    style Q fill:#d1fae5
    style R fill:#c7d2fe
    style M fill:#ddd6fe
```

## DeepAgent Pattern Implementation

```mermaid
graph TB
    subgraph "DeepAgent Pattern"
        direction TB
        
        subgraph "Planning Agent"
            P1[Analyze Request]
            P2[Determine Strategy]
            P3[Assess Risks]
            P4[Prepare Fallback]
        end
        
        subgraph "FileSystem Agent"
            F1[Locate Files]
            F2[Verify Access]
            F3[Read Content]
            F4[Parse Structure]
        end
        
        subgraph "SubAgent Orchestration"
            S1{Select Agent}
            S2[SpeedAnalyzer]
            S3[PrecisionAnalyzer]
            S4[Aggregate Results]
        end
        
        P1 --> P2 --> P3 --> P4
        P4 --> F1
        F1 --> F2 --> F3 --> F4
        F4 --> S1
        S1 -->|Fast| S2
        S1 -->|Accurate| S3
        S2 --> S4
        S3 --> S4
    end
    
    style P1 fill:#fef3c7
    style P2 fill:#fef3c7
    style P3 fill:#fef3c7
    style P4 fill:#fef3c7
    style F1 fill:#ddd6fe
    style F2 fill:#ddd6fe
    style F3 fill:#ddd6fe
    style F4 fill:#ddd6fe
    style S2 fill:#fecaca
    style S3 fill:#fed7aa
```

## SPEED Mode Internal Flow

```mermaid
graph LR
    A[Python Files] --> B[Tree-sitter<br/>Parser]
    B --> C[AST Nodes]
    C --> D[Extract<br/>Functions/Classes]
    C --> E[Extract<br/>Calls]
    
    D --> F[NetworkX<br/>DiGraph]
    E --> F
    
    F --> G[Target<br/>Symbol]
    G --> H[BFS<br/>Predecessors]
    H --> I[Depth<br/>Filter]
    I --> J[Impact<br/>Ranking]
    J --> K[Dependencies<br/>List]
    
    style B fill:#fca5a5
    style F fill:#fca5a5
    style H fill:#fca5a5
    style J fill:#fca5a5
```

## PRECISION Mode Internal Flow

```mermaid
graph LR
    A[Python Project] --> B{Pyright<br/>Check}
    B -->|Available| C[Start LSP<br/>Server]
    B -->|Not Available| N[Error +<br/>Fallback]
    
    C --> D[Index<br/>Project]
    D --> E[Find<br/>Symbol]
    E --> F[Query<br/>References]
    F --> G[Parse<br/>Locations]
    G --> H[Group by<br/>File]
    H --> I[Count<br/>References]
    I --> J[Impact<br/>Ranking]
    J --> K[Dependencies<br/>List]
    
    N --> M[Human-in-Loop]
    M --> O{Approve?}
    O -->|Yes| P[SPEED Mode]
    O -->|No| Q[Return Error]
    
    style C fill:#fdba74
    style D fill:#fdba74
    style F fill:#fdba74
    style J fill:#fdba74
    style M fill:#c4b5fd
```

## State Management in LangGraph

```mermaid
stateDiagram-v2
    [*] --> ValidateInput
    ValidateInput --> DecideMode: Input Valid
    ValidateInput --> [*]: Input Invalid
    
    DecideMode --> ExecuteAnalysis: Mode Selected
    
    ExecuteAnalysis --> Success: Analysis OK
    ExecuteAnalysis --> HandleFallback: Analysis Failed
    
    HandleFallback --> ExecuteAnalysis: Retry with SPEED
    HandleFallback --> [*]: Max Retries Reached
    
    Success --> [*]
    
    note right of ExecuteAnalysis
        Executes SpeedAnalyzer
        or PrecisionAnalyzer
        based on mode
    end note
    
    note right of HandleFallback
        Human-in-the-Loop
        approval process
    end note
```

## Complete System Overview

```mermaid
graph TB
    subgraph "External Systems"
        USER[User]
        ENV[Environment<br/>.env]
        FS[File System]
    end
    
    subgraph "Application Layer"
        CLI[CLI]
        API[API]
        LGS[LangGraph<br/>Studio]
    end
    
    subgraph "Workflow Layer"
        LG[LangGraph<br/>Workflow]
        NODES[Workflow<br/>Nodes]
    end
    
    subgraph "Business Logic"
        COORD[Coordinator]
        PLAN[Planning]
        FILESYS[FileSystem]
        SUBAGT[SubAgent]
    end
    
    subgraph "Analysis Layer"
        SPEED[SPEED<br/>Analyzer]
        PREC[PRECISION<br/>Analyzer]
    end
    
    subgraph "Infrastructure"
        TS[Tree-sitter]
        NX[NetworkX]
        LSP[Pyright<br/>LSP]
    end
    
    subgraph "Data Layer"
        MODELS[Data<br/>Models]
        RESULTS[Results<br/>Storage]
    end
    
    USER --> CLI
    USER --> API
    USER --> LGS
    
    ENV --> COORD
    FS --> FILESYS
    
    CLI --> LG
    API --> LG
    LGS --> LG
    
    LG --> NODES
    NODES --> COORD
    
    COORD --> PLAN
    COORD --> FILESYS
    COORD --> SUBAGT
    
    SUBAGT --> SPEED
    SUBAGT --> PREC
    
    SPEED --> TS
    SPEED --> NX
    PREC --> LSP
    
    TS --> MODELS
    NX --> MODELS
    LSP --> MODELS
    
    MODELS --> RESULTS
    RESULTS --> USER
```

---

## Legend

### Colors
- 🔵 **Blue**: User Interfaces (CLI, API, Studio)
- 🟢 **Green**: Coordinator & Business Logic
- 🔴 **Red**: SPEED Mode Components
- 🟠 **Orange**: PRECISION Mode Components
- 🟣 **Purple**: Human-in-the-Loop & Fallback

### Node Shapes
- **Rectangle**: Process/Component
- **Diamond**: Decision Point
- **Circle**: State
- **Hexagon**: External System

### Edge Styles
- **Solid Line**: Normal Flow
- **Dashed Line**: Fallback Flow
- **Dotted Line**: Optional Flow

---

## v0.2.0 Extended Architecture

### Advanced Agents System

```mermaid
graph TB
    subgraph "User Layer"
        USER[User]
        HUMAN[Human-in-Loop]
    end
    
    subgraph "Coordinator Layer"
        AC[AdvancedCoordinator<br/>Planning + SubAgent]
        IC[ImpactAnalysisCoordinator<br/>FR-IA]
    end
    
    subgraph "Agent Layer"
        FS[FileSystemAgent<br/>FR-FS<br/>FileSystemBackend]
        SH[SelfHealingAgent<br/>FR-AC<br/>Max 3 Retries]
        DOC[DocumentationAgent<br/>FR-DS<br/>Docstring+README+Swagger]
    end
    
    subgraph "Analyzer Layer"
        SPEED[SpeedAnalyzer<br/>Tree-sitter+NetworkX]
        PREC[PrecisionAnalyzer<br/>LSP/Pyright]
    end
    
    subgraph "DeepAgents Library"
        FSB[FileSystemBackend<br/>ls, read_file, glob,<br/>grep, edit_file, write_file]
    end
    
    subgraph "LLM Layer"
        GPT4O[GPT-4o<br/>Code Generation]
        GPT4OM[GPT-4o-mini<br/>Analysis & Summary]
    end
    
    USER --> AC
    USER --> IC
    
    AC --> FS
    AC --> SH
    AC --> DOC
    
    FS --> FSB
    FS --> GPT4OM
    
    SH --> GPT4O
    SH --> HUMAN
    
    DOC --> GPT4O
    DOC --> HUMAN
    
    IC --> SPEED
    IC --> PREC
    IC --> HUMAN
    
    SPEED --> GPT4OM
    PREC --> GPT4OM
    
    style AC fill:#d1fae5,stroke:#065f46
    style FS fill:#bfdbfe,stroke:#1e3a8a
    style SH fill:#fecaca,stroke:#b91c1c
    style DOC fill:#fef3c7,stroke:#78350f
    style FSB fill:#ddd6fe,stroke:#4c1d95
    style HUMAN fill:#fbcfe8,stroke:#831843
```

### Self-Healing Workflow

```mermaid
sequenceDiagram
    participant User
    participant SelfHealingAgent
    participant LLM
    participant Executor
    participant Human
    
    User->>SelfHealingAgent: Submit Buggy Code
    
    loop Max 3 Retries
        SelfHealingAgent->>Executor: Execute Code
        Executor->>SelfHealingAgent: Result + Error
        
        alt Success
            SelfHealingAgent->>User: Return Fixed Code
        else Error (Attempt < 3)
            SelfHealingAgent->>SelfHealingAgent: Analyze Error Type
            SelfHealingAgent->>LLM: Original Code + Error + Docs
            LLM->>SelfHealingAgent: Patch (Diff)
            SelfHealingAgent->>SelfHealingAgent: Apply Patch
        else Error (Attempt = 3)
            SelfHealingAgent->>Human: Max Retries Reached
            Human->>User: Show Healing History
            SelfHealingAgent->>User: Return Failure + History
        end
    end
```

### FileSystem Operations Flow

```mermaid
flowchart LR
    A[FileSystemAgent] --> B{Operation?}
    
    B -->|Explore| C[ls + LLM Insights]
    B -->|Search| D[glob + grep]
    B -->|Modify| E[edit_file]
    B -->|Create| F[write_file]
    B -->|Read| G{File Size?}
    
    G -->|Small| H[Direct Return]
    G -->|Large| I[Save + Summary]
    
    I --> J{Human Approval?}
    J -->|Yes| K[Process with SubAgent]
    J -->|No| L[Return Summary Only]
    
    C --> FSB[FileSystemBackend]
    D --> FSB
    E --> FSB
    F --> FSB
    
    style A fill:#bfdbfe
    style FSB fill:#ddd6fe
    style J fill:#fbcfe8
```

### Documentation Sync Workflow

```mermaid
stateDiagram-v2
    [*] --> DetectChanges
    DetectChanges --> AnalyzeAST: Old + New Code
    AnalyzeAST --> IdentifyNeeds: Functions/Classes Changed
    
    IdentifyNeeds --> UpdateDocstring: Docstring Needed
    IdentifyNeeds --> UpdateREADME: README Needed
    IdentifyNeeds --> UpdateSwagger: API Docs Needed
    
    UpdateDocstring --> GenerateProposal
    UpdateREADME --> GenerateProposal
    UpdateSwagger --> GenerateProposal
    
    GenerateProposal --> HumanApproval: auto_apply=False
    GenerateProposal --> ApplyChanges: auto_apply=True
    
    HumanApproval --> ApplyChanges: Approved
    HumanApproval --> [*]: Rejected
    
    ApplyChanges --> [*]: Complete
    
    note right of HumanApproval
        Human-in-the-Loop
        for critical decisions
    end note
```

### Integrated Workflow (AdvancedCoordinator)

```mermaid
flowchart TD
    Start[User Request] --> AC[AdvancedCoordinator]
    
    AC --> Step1[Step 1: Explore Context<br/>FileSystemAgent]
    Step1 --> Step2[Step 2: Analyze Impact<br/>ImpactAnalysisCoordinator]
    Step2 --> Step3[Step 3: Generate & Heal Code<br/>SelfHealingAgent]
    
    Step3 --> Check{Success?}
    Check -->|Yes| Step4[Step 4: Generate Tests<br/>SelfHealingAgent]
    Check -->|No| Report[Report Failure + History]
    
    Step4 --> Step5[Step 5: Sync Documentation<br/>DocumentationAgent]
    Step5 --> Human{Human Approval?}
    
    Human -->|Approve| Apply[Apply All Changes]
    Human -->|Reject| Review[Review Proposals]
    
    Apply --> End[Complete]
    Review --> End
    Report --> End
    
    style AC fill:#d1fae5
    style Human fill:#fbcfe8
    style Check fill:#fef3c7
```

---

## Component Responsibilities

### FileSystemAgent (FR-FS)
- **FR-FS-01**: Contextual exploration with `ls` and `read_file`
- **FR-FS-02**: Pattern search with `glob` and `grep`
- **FR-FS-03**: Code modification with `edit_file` and `write_file`
- **FR-FS-04**: Large output handling with caching and Human-in-Loop

### SelfHealingAgent (FR-AC)
- **FR-AC-01**: Refactoring execution based on impact analysis
- **FR-AC-02**: Self-healing loop (Execute → Analyze → Patch → Retry, Max 3)
- **FR-AC-03**: Automatic test generation (pytest/unittest)

### DocumentationAgent (FR-DS)
- **FR-DS-01**: Automatic documentation sync
  - Docstring generation and updates
  - README synchronization
  - Swagger/API documentation updates
  - AST-based change detection
  - Human-in-Loop approval

### AdvancedCoordinator
- **Planning**: Orchestrate complete workflow
- **FileSystem**: Integrate FileSystemAgent
- **SubAgent**: Delegate to specialized agents
- **Human-in-Loop**: Manage approval flow

---

## Technology Stack by Component

| Component | Technologies |
|-----------|-------------|
| **FileSystemAgent** | DeepAgents FileSystemBackend, GPT-4o-mini |
| **SelfHealingAgent** | GPT-4o, subprocess, pytest |
| **DocumentationAgent** | GPT-4o, AST parsing |
| **ImpactAnalysisCoordinator** | Tree-sitter, NetworkX, Pyright, GPT-4o-mini |
| **AdvancedCoordinator** | LangChain, async/await |

---

**버전**: 0.2.0  
**문서 인덱스**: [INDEX.md](INDEX.md)
