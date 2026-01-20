# Database Migrations

This folder contains SQL migration scripts for the Travel Lotara database.

## Setup Instructions

### 1. Create a Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign up / Log in
3. Click "New Project"
4. Choose your organization
5. Enter project details:
   - **Name**: `lotara-travel` (or your preferred name)
   - **Database Password**: Generate a strong password (save it!)
   - **Region**: Choose closest to your users
6. Click "Create new project"

### 2. Get Your API Keys

1. Go to **Project Settings** > **API**
2. Copy these values to your `.env` file:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** key → `SUPABASE_ANON_KEY`
   - **service_role** key → `SUPABASE_SERVICE_ROLE_KEY`

### 3. Run Migrations

1. Go to **SQL Editor** in your Supabase dashboard
2. Click "New query"
3. Copy and paste the contents of `001_initial_schema.sql`
4. Click "Run" (or press Ctrl/Cmd + Enter)

### 4. Verify Setup

After running migrations, you should see these tables:
- `jobs` - Workflow execution records
- `sessions` - User conversation context
- `feedback` - User ratings and comments
- `user_preferences` - Personalization data
- `itineraries` - Saved travel plans
- `health_check` - Connectivity test table

## Migration Files

| File | Description |
|------|-------------|
| `001_initial_schema.sql` | Initial database schema with all tables |

## Free Tier Considerations

Supabase free tier includes:
- 500MB database storage
- 2GB bandwidth
- 50,000 monthly active users
- 500MB file storage

### Optimizations Applied

1. **JSONB for flexible data**: Reduces need for schema changes
2. **Efficient indexes**: Only on frequently queried columns
3. **Message limits**: Sessions keep only last 50 messages
4. **Automatic cleanup**: Function to remove old inactive sessions

## Adding New Migrations

1. Create a new file: `002_your_migration_name.sql`
2. Add your SQL statements
3. Test in Supabase SQL Editor
4. Document changes in this README

## Rollback

To rollback, create a separate rollback script or use Supabase's backup feature:

1. Go to **Database** > **Backups**
2. Click on a previous backup
3. Click "Restore"

## Security Notes

- **Never commit** `.env` files with real API keys
- Use **service_role** key only on server-side
- Use **anon** key for client-side (with RLS enabled)
- Enable Row Level Security (RLS) for production
