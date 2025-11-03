# System Architecture Diagram

## High-Level Architecture

```mermaid
graph TB
    subgraph "User Interface"
        A[Claude Desktop/API]
    end
    
    subgraph "MCP Server"
        B[Bug Automation MCP]
        C[Playwright Parser]
        D[Google Sheets Client]
        E[GitLab Client]
        F[Playwright Browser]
    end
    
    subgraph "External Services"
        G[Google Sheets API]
        H[GitLab API]
        I[Web Application Under Test]
    end
    
    A <-->|MCP Protocol| B
    B --> C
    B --> D
    B --> E
    B --> F
    D <-->|REST API| G
    E <-->|REST API| H
    F <-->|Browser Automation| I
```

## Data Flow - Bug Reproduction

```mermaid
sequenceDiagram
    participant User
    participant Claude
    participant MCP Server
    participant Google Sheets
    participant Playwright
    participant WebApp
    
    User->>Claude: "Reproduce BUG-001"
    Claude->>MCP Server: read_bug("BUG-001")
    MCP Server->>Google Sheets: GET bug details
    Google Sheets-->>MCP Server: Bug data
    MCP Server-->>Claude: Bug information
    
    Claude->>MCP Server: reproduce_bug(BUG-001, steps)
    MCP Server->>Playwright: Launch browser
    Playwright->>WebApp: Navigate to URL
    loop For each step
        MCP Server->>Playwright: Execute step
        Playwright->>WebApp: Perform action
        WebApp-->>Playwright: Response
        Playwright->>Playwright: Capture screenshot
    end
    Playwright-->>MCP Server: Results + Screenshots
    MCP Server-->>Claude: Reproduction results
    Claude-->>User: "Bug reproduced successfully [screenshots]"
```

## Data Flow - Fix and Commit

```mermaid
sequenceDiagram
    participant User
    participant Claude
    participant MCP Server
    participant Playwright
    participant GitLab
    participant Google Sheets
    
    User->>Claude: "I fixed the bug, verify and commit"
    
    Claude->>MCP Server: verify_fix(BUG-001, steps)
    MCP Server->>Playwright: Run verification
    Playwright-->>MCP Server: Verification passed
    MCP Server-->>Claude: Fix verified
    
    Claude->>MCP Server: commit_fix(BUG-001, files)
    MCP Server->>GitLab: Create branch
    MCP Server->>GitLab: Commit files
    MCP Server->>GitLab: Create MR
    GitLab-->>MCP Server: MR URL
    
    MCP Server->>Google Sheets: Update status to "Fixed"
    Google Sheets-->>MCP Server: Confirmed
    
    MCP Server-->>Claude: All steps completed
    Claude-->>User: "Committed to GitLab, MR created, status updated"
```

## Component Interaction

```mermaid
graph LR
    subgraph "Core Components"
        A[MCP Server<br/>server.py]
        B[Step Parser<br/>playwright_parser.py]
    end
    
    subgraph "Tools"
        C[read_bug]
        D[reproduce_bug]
        E[verify_fix]
        F[commit_fix]
        G[update_bug_status]
    end
    
    subgraph "Resources"
        H[sheets://bugs/active]
        I[sheets://bugs/pending]
    end
    
    A --> C
    A --> D
    A --> E
    A --> F
    A --> G
    A --> H
    A --> I
    B -.->|Used by| D
    B -.->|Used by| E
```

## Playwright Step Parsing Flow

```mermaid
flowchart TD
    A[Receive Step] --> B{Parse Step Type}
    
    B -->|Navigation| C[Extract URL]
    B -->|Click| D[Extract Selector]
    B -->|Input| E[Extract Text & Selector]
    B -->|Verify| F[Extract Assertion]
    B -->|Wait| G[Extract Condition]
    
    C --> H[Execute Navigation]
    D --> I[Find Element]
    E --> J[Find Input & Fill]
    F --> K[Check Condition]
    G --> L[Wait for Event]
    
    I --> M{Found?}
    M -->|Yes| N[Click Element]
    M -->|No| O[Return Error]
    
    J --> P{Found?}
    P -->|Yes| Q[Fill Text]
    P -->|No| O
    
    K --> R{Passes?}
    R -->|Yes| S[Return Success]
    R -->|No| O
    
    H --> T[Capture Screenshot]
    N --> T
    Q --> T
    S --> T
    L --> T
    O --> T
    
    T --> U[Return Result]
```

## State Transitions

```mermaid
stateDiagram-v2
    [*] --> Open: Bug Created
    Open --> InProgress: Developer Starts
    Open --> Confirmed: Reproduction Successful
    Confirmed --> InProgress: Work Started
    InProgress --> Fixed: Fix Committed
    Fixed --> Verified: Verification Passed
    Fixed --> InProgress: Verification Failed
    Verified --> Closed: Approved
    Closed --> [*]
    
    note right of Confirmed
        Automated by
        reproduce_bug tool
    end note
    
    note right of Fixed
        Automated by
        commit_fix tool
    end note
    
    note right of Verified
        Automated by
        verify_fix tool
    end note
```

## Google Sheets Schema

```mermaid
erDiagram
    BUGS {
        string bug_id PK
        string title
        text description
        text reproduction_steps
        string expected_result
        string actual_result
        string status
        string priority
        text notes
        datetime created_at
        datetime updated_at
    }
    
    BUGS ||--o{ REPRODUCTIONS : has
    BUGS ||--o{ VERIFICATIONS : has
    BUGS ||--o{ COMMITS : has
    
    REPRODUCTIONS {
        string bug_id FK
        datetime attempted_at
        boolean success
        text error_message
        binary screenshots
    }
    
    VERIFICATIONS {
        string bug_id FK
        datetime verified_at
        boolean passed
        text results
    }
    
    COMMITS {
        string bug_id FK
        string branch_name
        string commit_sha
        string mr_url
        datetime committed_at
    }
```

## Security Model

```mermaid
flowchart TB
    subgraph "Authentication"
        A[Service Account<br/>credentials.json]
        B[GitLab Token<br/>Personal Access Token]
    end
    
    subgraph "Authorization"
        C[Google Sheets<br/>Reader/Writer]
        D[GitLab Project<br/>Developer Role]
    end
    
    subgraph "Secure Storage"
        E[Environment Variables<br/>.env file]
        F[Never in Git<br/>.gitignore]
    end
    
    A --> C
    B --> D
    C --> E
    D --> E
    E --> F
    
    style F fill:#f99,stroke:#333,stroke-width:2px
```

## Deployment Options

```mermaid
graph TB
    subgraph "Local Development"
        A[Python Script]
        B[Claude Desktop]
    end
    
    subgraph "Server Deployment"
        C[Docker Container]
        D[Cloud VM]
        E[CI/CD Pipeline]
    end
    
    subgraph "Scaling"
        F[Multiple Workers]
        G[Playwright Grid]
        H[Message Queue]
    end
    
    A --> C
    B --> C
    C --> F
    D --> F
    E --> F
    F --> G
    F --> H
```

## Tool Call Sequence

```mermaid
sequenceDiagram
    autonumber
    
    participant Claude
    participant MCP
    participant Sheets
    participant Playwright
    participant GitLab
    
    Note over Claude,GitLab: Complete Bug Resolution Flow
    
    Claude->>MCP: list_resources()
    MCP-->>Claude: [active_bugs, pending_bugs]
    
    Claude->>MCP: read_resource(sheets://bugs/active)
    MCP->>Sheets: API call
    Sheets-->>MCP: Bug list
    MCP-->>Claude: Formatted bug data
    
    Claude->>MCP: read_bug(bug_id)
    MCP->>Sheets: Get specific bug
    Sheets-->>MCP: Bug details
    MCP-->>Claude: Full bug info
    
    Claude->>MCP: reproduce_bug(bug_id, url, steps)
    MCP->>Playwright: Launch & execute
    Playwright-->>MCP: Screenshots + results
    MCP-->>Claude: Reproduction report
    
    Note over Claude: Developer fixes code
    
    Claude->>MCP: verify_fix(bug_id, url, steps)
    MCP->>Playwright: Run verification
    Playwright-->>MCP: Verification results
    MCP-->>Claude: Pass/Fail status
    
    Claude->>MCP: commit_fix(bug_id, branch, files, message)
    MCP->>GitLab: Create branch
    MCP->>GitLab: Commit files
    MCP->>GitLab: Create MR
    GitLab-->>MCP: MR details
    MCP-->>Claude: Commit confirmation
    
    Claude->>MCP: update_bug_status(bug_id, "Fixed")
    MCP->>Sheets: Update status
    Sheets-->>MCP: Confirmation
    MCP-->>Claude: Status updated
```

## Error Handling Flow

```mermaid
flowchart TD
    A[Execute Tool] --> B{Success?}
    B -->|Yes| C[Return Results]
    B -->|No| D{Error Type}
    
    D -->|Network| E[Retry with Backoff]
    D -->|Authentication| F[Return Auth Error]
    D -->|Element Not Found| G[Capture Screenshot]
    D -->|Timeout| H[Return Timeout Error]
    
    E --> I{Retry Success?}
    I -->|Yes| C
    I -->|No| J[Return Error + Details]
    
    F --> J
    G --> J
    H --> J
    
    J --> K[Log Error]
    K --> L[Notify User]
```

## Legend

- **MCP Protocol**: Model Context Protocol for communication
- **REST API**: Standard HTTP REST endpoints
- **Browser Automation**: Playwright WebDriver protocol
- **Async/Await**: All operations are asynchronous
- **Error Handling**: Comprehensive error catching and reporting
- **Screenshots**: Captured at key points for debugging

---

These diagrams show the complete system architecture and data flows. Use them to:
- Understand component interactions
- Debug issues
- Plan enhancements
- Onboard new developers
