# Backend Architect Build Spec - Systematic Recovery Plan

## Current State Analysis

### Issues Identified
1. **Docker Desktop Instability**: Daemon quits after startup, no persistence
2. **Working Directory Confusion**: Commands executing in USB drive instead of Mac
3. **No Automated Health Checks**: Manual verification only
4. **Sequential Processing**: Tools installed one-by-one instead of parallel
5. **No Cloud Workspace**: No remote development environment
6. **No Fallback Strategy**: Single point of failure on Docker

### Root Causes
- Docker Desktop 4.24.2 installed but daemon not persistent
- Manual GUI startup without service management
- No automated daemon verification loop
- Context switching overhead between directories
- Lack of systematic build process

## Systematic Build Spec

### Phase 1: Infrastructure Foundation (Priority: CRITICAL)

#### 1.1 Establish Permanent Working Context
- **Action**: Always work in `/opt/agents` directory
- **Verification**: `cd /opt/agents && pwd` before every command
- **Prevention**: Add directory check to command execution

#### 1.2 Docker Daemon Service Setup
- **Action**: Implement automated Docker daemon health check
- **Implementation**: 
  ```bash
  # Health check script
  function docker_health_check() {
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
      if docker ps > /dev/null 2>&1; then
        return 0
      fi
      attempt=$((attempt + 1))
      sleep 2
    done
    return 1
  }
  ```
- **Fallback**: If Docker fails, use alternative container solution

#### 1.3 Cloud Workspace Setup
- **Action**: Create cloud workspace with GitHub repo
- **Implementation**: Set up Codespaces or similar remote environment
- **Benefit**: Eliminates local environment issues

### Phase 2: Container Infrastructure (Priority: HIGH)

#### 2.1 Docker Daemon Verification
- **Action**: Automated daemon startup and verification
- **Implementation**:
  ```bash
  cd /opt/agents
  open /Applications/Docker.app
  docker_health_check
  docker ps
  ```

#### 2.2 PostgreSQL Container Setup
- **Action**: Configure PostgreSQL with persistence
- **Implementation**:
  ```bash
  docker run -d \
    --name postgres \
    -e POSTGRES_PASSWORD=postgres \
    -p 5432:5432 \
    -v postgres_data:/var/lib/postgresql/data \
    postgres:15
  ```

#### 2.3 Redis Container Setup
- **Action**: Configure Redis with persistence
- **Implementation**:
  ```bash
  docker run -d \
    --name redis \
    -p 6379:6379 \
    -v redis_data:/data \
    redis:7-alpine
  ```

### Phase 3: Tool Installation (Priority: MEDIUM)

#### 3.1 Builder.io CLI
- **Action**: Install builder.io CLI
- **Implementation**: `npx builder.io@latest launch`

#### 3.2 VSCode CLI Setup
- **Action**: Find VSCode installation and add to PATH
- **Implementation**:
  ```bash
  find /Applications -name "Visual Studio Code.app"
  export PATH="$PATH:/Applications/Visual Studio Code.app/Contents/Resources/app/bin"
  ```

#### 3.3 VSCode Extensions
- **Action**: Install documentation-assembler-vsix and Mobile Deck
- **Implementation**: Use code CLI once PATH is set

#### 3.4 Xtro Alternative
- **Action**: Research Mobile Deck + Mobile MCP as Xtro alternative
- **Implementation**: Use Mobile MCP for mobile IDE control

### Phase 4: Application Development (Priority: MEDIUM)

#### 4.1 Desktop App Rebuild
- **Action**: Rebuild with interactive coding/business/cyber recovery features
- **Implementation**: Enhance Tauri app with comprehensive dashboard

#### 4.2 Automation Workflows
- **Action**: Create Mac and mainframe automation workflows
- **Implementation**: Document and script automated processes

## Execution Order

1. ✅ Establish `/opt/agents` as working directory
2. ⏳ Implement Docker daemon health check
3. ⏳ Start and verify Docker Desktop
4. ⏳ Configure PostgreSQL container
5. ⏳ Configure Redis container
6. ⏳ Install builder.io CLI
7. ⏳ Set up VSCode CLI
8. ⏳ Install VSCode extensions
9. ⏳ Find Xtro alternative
10. ⏳ Rebuild desktop app
11. ⏳ Create automation workflows
12. ⏳ Set up cloud workspace

## Success Criteria

- Docker daemon running persistently
- PostgreSQL container accessible on port 5432
- Redis container accessible on port 6379
- All CLI tools installed and functional
- VSCode extensions installed
- Desktop app with interactive features
- Cloud workspace active
- Automation workflows documented

## Anti-Patterns to Avoid

- ❌ Working in USB drive for active development
- ❌ Manual Docker daemon verification
- ❌ Sequential tool installation
- ❌ No fallback strategies
- ❌ No automated health checks
- ❌ Single point of failure

## Best Practices

- ✅ Always verify working directory
- ✅ Use automated health checks
- ✅ Parallel compatible operations
- ✅ Implement fallback strategies
- ✅ Document all processes
- ✅ Test each phase before proceeding
