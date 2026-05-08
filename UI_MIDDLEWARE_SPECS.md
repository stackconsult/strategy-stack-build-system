# UI and Middleware Wiring Specifications
# 19-Agent Build System

## Frontend-Middleware-Database Architecture

### Database Schema Mapping to UI Components

#### 1. Builds Table → Build Dashboard

**Database Fields:**
- `build_id` (VARCHAR, PK) → Build ID Display
- `status` (VARCHAR) → Status Badge (PENDING/ACTIVE/COMPLETED/FAILED)
- `current_phase` (INTEGER) → Phase Progress Indicator
- `prd_path` (TEXT) → PRD Link Display
- `metadata` (JSONB) → Build Configuration Panel
- `started_at` (TIMESTAMP) → Start Time Display
- `completed_at` (TIMESTAMP) → Completion Time Display
- `created_at` (TIMESTAMP) → Created Time Display

**UI Component:**
```typescript
interface BuildDashboardProps {
  buildId: string;
  status: 'PENDING' | 'ACTIVE' | 'COMPLETED' | 'FAILED';
  currentPhase: number;
  prdPath: string;
  metadata: Record<string, any>;
  startedAt: string;
  completedAt: string | null;
  createdAt: string;
}
```

**Middleware API:**
```typescript
GET /api/builds/:build_id
POST /api/builds/start
GET /api/builds
```

#### 2. Events Table → Activity Feed

**Database Fields:**
- `event_id` (SERIAL, PK) → Event ID
- `build_id` (VARCHAR, FK) → Build Reference
- `agent_type` (VARCHAR) → Agent Icon/Label
- `agent_version` (VARCHAR) → Agent Version Badge
- `event_type` (VARCHAR) → Event Type Badge
- `event_data` (JSONB) → Event Details Panel
- `timestamp_utc` (TIMESTAMP) → Timestamp Display

**UI Component:**
```typescript
interface ActivityFeedProps {
  events: Array<{
    eventId: number;
    buildId: string;
    agentType: string;
    agentVersion: string;
    eventType: string;
    eventData: Record<string, any>;
    timestampUtc: string;
  }>;
}
```

**Middleware API:**
```typescript
GET /api/builds/:build_id/events
GET /api/events
```

#### 3. Gates Table → Gates Progress Tracker

**Database Fields:**
- `gate_id` (VARCHAR, PK) → Gate ID Display
- `gate_name` (VARCHAR) → Gate Name
- `gate_description` (TEXT) → Gate Description Tooltip
- `phase` (INTEGER) → Phase Number
- `gate_status` (VARCHAR) → Gate Status Badge
- `created_at` (TIMESTAMP) → Gate Creation Time

**UI Component:**
```typescript
interface GatesTrackerProps {
  gates: Array<{
    gateId: string;
    gateName: string;
    gateDescription: string;
    phase: number;
    gateStatus: 'PENDING' | 'PASSED' | 'FAILED';
    createdAt: string;
  }>;
}
```

**Middleware API:**
```typescript
GET /api/gates
POST /api/gates/:gate_id/pass
```

#### 4. Blockers Table → Blockers Panel

**Database Fields:**
- `blocker_id` (SERIAL, PK) → Blocker ID
- `build_id` (VARCHAR, FK) → Build Reference
- `gate_id` (VARCHAR, FK) → Gate Reference
- `blocker_type` (VARCHAR) → Blocker Type Badge
- `blocker_description` (TEXT) → Blocker Description
- `resolved` (BOOLEAN) → Resolved Status
- `resolved_at` (TIMESTAMP) → Resolution Time
- `created_at` (TIMESTAMP) → Creation Time

**UI Component:**
```typescript
interface BlockersPanelProps {
  blockers: Array<{
    blockerId: number;
    buildId: string;
    gateId: string | null;
    blockerType: string;
    blockerDescription: string;
    resolved: boolean;
    resolvedAt: string | null;
    createdAt: string;
  }>;
}
```

**Middleware API:**
```typescript
GET /api/blockers/:build_id
POST /api/blockers/:blocker_id/resolve
```

#### 5. Messages Table → Agent Communication Panel

**Database Fields:**
- `message_id` (SERIAL, PK) → Message ID
- `build_id` (VARCHAR, FK) → Build Reference
- `from_agent` (VARCHAR) → Sender Agent
- `to_agent` (VARCHAR) → Recipient Agent
- `message_content` (TEXT) → Message Content
- `message_type` (VARCHAR) → Message Type Badge
- `timestamp_utc` (TIMESTAMP) → Timestamp

**UI Component:**
```typescript
interface AgentCommunicationProps {
  messages: Array<{
    messageId: number;
    buildId: string;
    fromAgent: string;
    toAgent: string;
    messageContent: string;
    messageType: string;
    timestampUtc: string;
  }>;
}
```

**Middleware API:**
```typescript
GET /api/messages/:build_id
POST /api/messages/send
```

#### 6. Agent Heartbeats Table → Agent Status Monitor

**Database Fields:**
- `heartbeat_id` (SERIAL, PK) → Heartbeat ID
- `agent_type` (VARCHAR) → Agent Type
- `agent_version` (VARCHAR) → Agent Version
- `build_id` (VARCHAR, FK) → Build Reference
- `status` (VARCHAR) → Status Badge
- `last_seen` (TIMESTAMP) → Last Seen Time
- `metadata` (JSONB) → Agent Metadata

**UI Component:**
```typescript
interface AgentStatusMonitorProps {
  heartbeats: Array<{
    heartbeatId: number;
    agentType: string;
    agentVersion: string;
    buildId: string;
    status: string;
    lastSeen: string;
    metadata: Record<string, any>;
  }>;
}
```

**Middleware API:**
```typescript
GET /api/agents/status
GET /api/agents/:agent_type/status
```

## Frontend Component Architecture

### Desktop App (Tauri + React)

**Main Dashboard Layout:**
```
┌─────────────────────────────────────────┐
│ Header: Logo | Build Selector | Actions │
├─────────────────────────────────────────┤
│ Sidebar:                                │
│ • Builds List                          │
│ • Activity Feed                        │
│ • Gates Tracker                        │
│ • Blockers Panel                       │
│ • Agent Status                         │
├─────────────────────────────────────────┤
│ Main Content Area:                      │
│ • Build Details                        │
│ • Phase Progress                        │
│ • Agent Communication                   │
│ • Real-time Logs                       │
└─────────────────────────────────────────┘
```

### Real-time Updates via WebSocket

**WebSocket Endpoints:**
- `ws://localhost:8008/ws/builds/:build_id` - Build status updates
- `ws://localhost:8008/ws/events` - Event stream
- `ws://localhost:8008/ws/agents` - Agent status updates

### API Response Formats

**Standard Response:**
```json
{
  "success": true,
  "data": { /* actual data */ },
  "error": null,
  "timestamp": "2026-05-07T20:00:00Z"
}
```

**Error Response:**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "DATABASE_CONNECTION_ERROR",
    "message": "Failed to connect to database",
    "details": { /* additional context */ }
  },
  "timestamp": "2026-05-07T20:00:00Z"
}
```

## Middleware Layer (FastAPI)

### API Endpoints

**Build Management:**
- `POST /api/builds/start` - Start new build
- `GET /api/builds/:build_id` - Get build details
- `GET /api/builds` - List all builds
- `GET /api/builds/:build_id/status` - Get build status

**Event Management:**
- `GET /api/builds/:build_id/events` - Get build events
- `GET /api/events` - Get all events

**Gate Management:**
- `GET /api/gates` - Get all gates
- `POST /api/gates/:gate_id/pass` - Mark gate as passed

**Blocker Management:**
- `GET /api/blockers/:build_id` - Get build blockers
- `POST /api/blockers/:blocker_id/resolve` - Resolve blocker

**Message Management:**
- `GET /api/messages/:build_id` - Get build messages
- `POST /api/messages/send` - Send message between agents

**Agent Management:**
- `GET /api/agents/status` - Get all agent statuses
- `GET /api/agents/:agent_type/status` - Get specific agent status

### Database Connection Strategy

**Primary: Supabase Cloud PostgreSQL**
- Connection string from environment variable `DATABASE_URL`
- Automatic fallback to local PostgreSQL if unavailable
- Connection pooling via asyncpg

**Cache Layer: Redis**
- Session management
- Real-time pub/sub for WebSocket updates
- Temporary data storage

### Error Handling Strategy

**Database Errors:**
- Retry logic with exponential backoff
- Fallback to local PostgreSQL if Supabase unavailable
- Graceful degradation for read-only operations

**Network Errors:**
- Automatic reconnection for WebSocket
- Queue messages for later delivery
- Offline mode support

## State Management

### Frontend State (React Context)

```typescript
interface AppState {
  currentBuild: Build | null;
  builds: Build[];
  events: Event[];
  gates: Gate[];
  blockers: Blocker[];
  messages: Message[];
  agentStatuses: AgentStatus[];
  isConnected: boolean;
  databaseStatus: 'connected' | 'disconnected' | 'fallback';
}
```

### Real-time Synchronization

**WebSocket Message Types:**
- `BUILD_STATUS_UPDATE` - Build status changed
- `EVENT_CREATED` - New event created
- `GATE_PASSED` - Gate passed
- `BLOCKER_RAISED` - New blocker
- `BLOCKER_RESOLVED` - Blocker resolved
- `MESSAGE_RECEIVED` - New message
- `AGENT_STATUS_UPDATE` - Agent status changed

## Security Considerations

**Authentication:**
- JWT tokens for API authentication
- Supabase Auth integration for user management
- Role-based access control

**Data Validation:**
- Input validation on all API endpoints
- SQL injection prevention via parameterized queries
- XSS protection in React components

**Rate Limiting:**
- API rate limiting per user
- WebSocket connection limits
- Database query timeouts

## Performance Optimization

**Caching Strategy:**
- Redis caching for frequently accessed data
- Client-side caching for build lists
- Lazy loading for large datasets

**Query Optimization:**
- Database indexing on foreign keys
- Pagination for large result sets
- Query result caching

**Frontend Optimization:**
- Virtual scrolling for large lists
- Debounced search inputs
- Code splitting for lazy loading

## Deployment Configuration

**Environment Variables:**
```env
DATABASE_URL=postgresql://postgres:password@db.project.supabase.co:5432/postgres
SUPABASE_PROJECT_REF=project_ref
SUPABASE_DB_PASSWORD=password
REDIS_HOST=localhost
REDIS_PORT=6379
ORCHESTRATOR_HOST=localhost
ORCHESTRATOR_PORT=8008
```

**Development vs Production:**
- Development: Local PostgreSQL + Redis
- Production: Supabase + Redis (or Supabase Edge Functions)
- Staging: Supabase staging project

## Monitoring and Observability

**Metrics to Track:**
- Build completion time
- Agent execution time
- Database query performance
- WebSocket message latency
- Error rates by endpoint

**Logging Strategy:**
- Structured logging with correlation IDs
- Log aggregation via Supabase Logs
- Error tracking via Sentry (optional)
