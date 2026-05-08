# Supabase CLI Workflows for 19-Agent Build System
# Following Supabase CLI Documentation to Prevent Failures

## Overview

This document defines workflows that follow the official Supabase CLI documentation (https://supabase.com/docs/reference/cli/start) to ensure reliable database operations without failures. These workflows are designed to work with the 19-Agent Build System and integrate with the orchestrator and agents.

## Prerequisites

### Installation

```bash
# Install Supabase CLI via Homebrew (macOS)
brew install supabase/tap/supabase-beta

# Verify installation
supabase --version
```

### Authentication

```bash
# Login to Supabase
supabase login

# This will open browser for authentication
# Store access token securely
```

### Project Setup

```bash
# Link to existing project
supabase link --project-ref <project-ref>

# Or create new project
supabase projects create <project-name> \
  --org-id <org-id> \
  --db-password <password> \
  --region <region>
```

## Database Initialization Workflow

### Step 1: Initialize Local Development

```bash
# Initialize Supabase in project directory
cd ~/Desktop/19-agent-workspace
supabase init

# This creates:
# - supabase/config.toml
# - supabase/migrations/
# - supabase/functions/
```

### Step 2: Start Local Development

```bash
# Start local Supabase stack
supabase start

# This starts:
# - PostgreSQL (port 54322)
# - Studio (port 54323)
# - Gotrue (port 54324)
# - Realtime (port 54325)
# - Storage (port 54326)
# - Edge Functions (port 54327)
# - Kong (port 54328)
```

### Step 3: Create Database Schema

```bash
# Create migration file
supabase migration new init_governance_db

# Edit migration file
vim supabase/migrations/<timestamp>_init_governance_db.sql

# Apply migration
supabase db reset
```

### Step 4: Seed Data

```bash
# Create seed migration
supabase migration new seed_gates

# Edit seed file
vim supabase/migrations/<timestamp>_seed_gates.sql

# Apply migration
supabase db push
```

## Migration Management Workflow

### Creating Migrations

```bash
# Create new migration
supabase migration new <migration-name>

# Example:
supabase migration new add_builds_table

# This creates: supabase/migrations/<timestamp>_<name>.sql
```

### Applying Migrations

```bash
# Push migrations to remote project
supabase db push

# This:
# 1. Validates migration files
# 2. Applies migrations in order
# 3. Verifies schema consistency
# 4. Updates migration history
```

### Resetting Database

```bash
# Reset local database (DESTRUCTIVE)
supabase db reset

# This:
# 1. Drops all tables
# 2. Reapplies all migrations
# 3. Seeds initial data
# ⚠️ WARNING: Deletes all data
```

### Migration Best Practices

**DO:**
- Create descriptive migration names
- Write idempotent SQL
- Test migrations locally first
- Use transactions for complex changes
- Document breaking changes

**DON'T:**
- Modify existing migration files
- Skip migration numbers
- Mix DDL and DML in same migration
- Use hardcoded environment-specific values
- Forget to add NOT NULL constraints with defaults

## Remote Database Operations

### Connecting to Remote Database

```bash
# Generate connection string
supabase db dump -f backup.sql

# Or use connection string directly
DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"
```

### Remote Schema Changes

```bash
# Push local migrations to remote
supabase db push

# Pull remote schema to local
supabase db pull

# Diff local vs remote
supabase db diff
```

### Backup and Restore

```bash
# Backup remote database
supabase db dump -f backup.sql

# Restore to local
supabase db reset
psql -h localhost -p 54322 -U postgres -d postgres -f backup.sql

# Restore to remote (careful!)
psql $DATABASE_URL -f backup.sql
```

## Edge Functions Workflow

### Creating Edge Functions

```bash
# Create new edge function
supabase functions new <function-name>

# Example:
supabase functions new build-processor

# This creates:
# - supabase/functions/<function-name>/index.ts
# - supabase/functions/<function-name>/deno.json
```

### Deploying Edge Functions

```bash
# Deploy function to remote
supabase functions deploy <function-name>

# Deploy with environment variables
supabase functions deploy <function-name> \
  --env-var MY_VAR=value

# Deploy all functions
supabase functions deploy
```

### Local Function Development

```bash
# Start local development
supabase functions serve

# This serves functions at:
# http://localhost:54323/functions/v1/<function-name>
```

## Storage Management Workflow

### Creating Storage Buckets

```bash
# Create bucket via SQL migration
supabase migration new create_storage_buckets

# Add to migration:
-- Create storage bucket
INSERT INTO storage.buckets (id, name, public)
VALUES ('builds', 'builds', false);

-- Create policies
CREATE POLICY "Public Access"
ON storage.objects FOR SELECT
TO anon
USING (bucket_id = 'builds');
```

### Managing Files

```bash
# Upload file via API (not CLI)
# Use Supabase client SDK or REST API

# List files via SQL
SELECT * FROM storage.objects WHERE bucket_id = 'builds';
```

## Row Level Security (RLS) Workflow

### Enabling RLS

```bash
# Create migration for RLS
supabase migration new enable_rls

# Add to migration:
-- Enable RLS on all tables
ALTER TABLE builds ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE gates ENABLE ROW LEVEL SECURITY;
-- ... other tables
```

### Creating Policies

```bash
# Create policy migration
supabase migration new create_policies

# Add policies:
-- Builds table policies
CREATE POLICY "Users can view their builds"
ON builds FOR SELECT
TO authenticated
USING (auth.uid()::text = metadata->>'user_id');

CREATE POLICY "Users can insert their builds"
ON builds FOR INSERT
TO authenticated
WITH CHECK (auth.uid()::text = metadata->>'user_id');
```

## Realtime Workflow

### Enabling Realtime

```bash
# Create migration for realtime
supabase migration new enable_realtime

# Add to migration:
-- Enable realtime on tables
ALTER PUBLICATION supabase_realtime ADD TABLE builds;
ALTER PUBLICATION supabase_realtime ADD TABLE events;
ALTER PUBLICATION supabase_realtime ADD TABLE agent_heartbeats;
```

### Subscribing to Changes

```typescript
// In agent code
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(DATABASE_URL)

// Subscribe to build changes
supabase
  .channel('build-updates')
  .on('postgres_changes', { event: '*', schema: 'public', table: 'builds' }, payload => {
    console.log('Build changed:', payload)
  })
  .subscribe()
```

## Agent Integration Workflow

### DO_AGENT_V1: Infrastructure Setup

```bash
# Workflow for setting up database infrastructure

# 1. Initialize Supabase project
supabase projects create strategy-stack-build-system \
  --org-id <org-id> \
  --db-password agents_secure_pass_2026 \
  --region us-east-2

# 2. Link project
supabase link --project-ref asaajoefhifdqhprowek

# 3. Initialize local development
cd ~/Desktop/19-agent-workspace
supabase init

# 4. Create schema migration
supabase migration new init_schema

# 5. Apply schema
supabase db push

# 6. Verify connection
supabase status
```

### BE_AGENT_V1: Database Operations

```python
# Agent code pattern for database operations

import os
from dotenv import load_dotenv
import asyncpg

load_dotenv()

# Get connection details
project_ref = os.getenv('SUPABASE_PROJECT_REF')
password = os.getenv('SUPABASE_DB_PASSWORD')

# Create connection pool
pool = await asyncpg.create_pool(
    user='postgres',
    password=password,
    database='postgres',
    host=f'db.{project_ref}.supabase.co',
    port=5432
)

# Execute queries
async with pool.acquire() as conn:
    result = await conn.fetch('SELECT * FROM builds')
```

### All Agents: Fallback Strategy

```python
# Universal fallback pattern for all agents

async def get_database_connection():
    """Get database connection with fallback"""
    try:
        # Try Supabase first
        if os.getenv('DATABASE_URL'):
            return await asyncpg.create_pool(os.getenv('DATABASE_URL'))
    except Exception as e:
        log.warning("supabase_failed", error=str(e))
    
    # Fallback to local PostgreSQL
    try:
        return await asyncpg.create_pool(
            user="agents_user",
            password="agents_secure_pass_2026",
            database="governance_db",
            host="localhost"
        )
    except Exception as local_error:
        log.error("local_postgresql_failed", error=str(local_error))
        raise
```

## Error Handling Workflow

### Connection Failures

```python
# Retry logic with exponential backoff

import asyncio
from datetime import datetime, timedelta

async def execute_with_retry(query, max_retries=3):
    """Execute query with retry logic"""
    for attempt in range(max_retries):
        try:
            async with pool.acquire() as conn:
                return await conn.fetch(query)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # Exponential backoff
            log.warning("query_failed_retry", error=str(e), attempt=attempt+1, wait=wait_time)
            await asyncio.sleep(wait_time)
```

### Migration Failures

```bash
# If migration fails, diagnose and fix

# 1. Check migration status
supabase migration list

# 2. View specific migration
supabase migration show <migration-id>

# 3. Fix migration file
vim supabase/migrations/<timestamp>_<name>.sql

# 4. Reset and reapply (DESTRUCTIVE)
supabase db reset

# 5. Or create new migration to fix issue
supabase migration new fix_previous_migration
```

## CI/CD Integration Workflow

### GitHub Actions Example

```yaml
name: Deploy Database Changes

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Supabase CLI
        run: |
          brew install supabase/tap/supabase-beta
          
      - name: Link to project
        run: |
          supabase link --project-ref ${{ secrets.SUPABASE_PROJECT_REF }}
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
          
      - name: Push migrations
        run: |
          supabase db push
        env:
          SUPABASE_DB_PASSWORD: ${{ secrets.SUPABASE_DB_PASSWORD }}
```

## Monitoring Workflow

### Health Checks

```bash
# Check local Supabase status
supabase status

# Check remote project status
supabase projects list

# Check database logs
supabase logs db --project-ref <project-ref>
```

### Performance Monitoring

```sql
-- Query slow queries
SELECT 
  query,
  calls,
  total_time,
  mean_time,
  max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Check connection pool
SELECT 
  count(*) as active_connections
FROM pg_stat_activity
WHERE state = 'active';
```

## Backup Workflow

### Automated Backups

```bash
# Create backup script
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_${DATE}.sql"

# Backup remote database
supabase db dump -f $BACKUP_FILE

# Upload to storage (using rclone or similar)
rclone copy $BACKUP_FILE remote:backups/

# Keep last 7 days
find . -name "backup_*.sql" -mtime +7 -delete
```

### Restore Workflow

```bash
# Restore from backup
# 1. Stop local development
supabase stop

# 2. Restore database
psql -h localhost -p 54322 -U postgres -d postgres -f backup.sql

# 3. Start local development
supabase start

# 4. Verify
supabase db diff
```

## Troubleshooting Workflow

### Common Issues

**Issue: Connection timeout**
```bash
# Solution: Check network connectivity
ping db.<project-ref>.supabase.co

# Check if project is paused
supabase projects list
# If paused, unpause in dashboard
```

**Issue: Migration conflict**
```bash
# Solution: Check migration history
supabase migration list

# Reset to known good state
supabase db reset

# Or create new migration to resolve
supabase migration new resolve_conflict
```

**Issue: Permission denied**
```bash
# Solution: Check user permissions
supabase db execute "SELECT current_user;"

# Grant necessary permissions
supabase db execute "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;"
```

## Best Practices Summary

### Development Workflow

1. **Always develop locally first** - Use `supabase start` for local development
2. **Test migrations locally** - Verify with `supabase db diff` before pushing
3. **Use version control** - Commit migration files with code changes
4. **Document breaking changes** - Add comments to migration files
5. **Backup before major changes** - Create backup before schema changes

### Production Workflow

1. **Use environment variables** - Never hardcode credentials
2. **Enable RLS** - Always use Row Level Security
3. **Monitor connections** - Watch connection pool usage
4. **Set up alerts** - Monitor database performance
5. **Have rollback plan** - Know how to revert changes

### Agent Integration

1. **Use fallback connections** - Always have local PostgreSQL fallback
2. **Implement retry logic** - Handle transient failures gracefully
3. **Log all database operations** - Enable structured logging
4. **Use connection pooling** - Reuse connections efficiently
5. **Close connections properly** - Clean up resources

## Quick Reference

### Essential Commands

```bash
# Authentication
supabase login
supabase logout

# Project Management
supabase projects create <name> --org-id <id> --db-password <pass> --region <region>
supabase projects list
supabase link --project-ref <ref>

# Local Development
supabase init
supabase start
supabase stop
supabase status

# Database Operations
supabase migration new <name>
supabase db push
supabase db reset
supabase db diff
supabase db dump -f backup.sql

# Edge Functions
supabase functions new <name>
supabase functions deploy <name>
supabase functions serve

# Logs
supabase logs db --project-ref <ref>
supabase logs functions --project-ref <ref>
```

### Environment Variables

```env
SUPABASE_PROJECT_REF=asaajoefhifdqhprowek
SUPABASE_DB_PASSWORD=agents_secure_pass_2026
DATABASE_URL=postgresql://postgres:agents_secure_pass_2026@db.asaajoefhifdqhprowek.supabase.co:5432/postgres
SUPABASE_ACCESS_TOKEN=<your-access-token>
```

## Conclusion

These workflows follow the official Supabase CLI documentation to ensure reliable database operations. By following these patterns, the 19-Agent Build System can:
- Initialize databases correctly
- Apply migrations safely
- Handle connection failures gracefully
- Integrate Supabase with agent workflows
- Maintain data consistency across environments

The key to success is to always develop locally first, test thoroughly, and have fallback mechanisms in place. These workflows provide the foundation for robust database operations in the build system.
