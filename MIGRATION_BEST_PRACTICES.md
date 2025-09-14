# Migration Best Practices for BottlePlug

## 🎯 Overview

This document outlines the proper migration practices implemented for the BottlePlug project to ensure clean, maintainable database schema management.

## 🔧 Current Implementation

### Clean Migration Fix Script

The `backend/scripts/proper_migration_fix.py` script implements a comprehensive approach to resolve migration conflicts:

1. **Database Backup**: Creates a backup before making changes
2. **Migration State Reset**: Clears problematic migration records
3. **Clean Migration Run**: Applies migrations in proper order
4. **Superuser Creation**: Ensures admin access is available
5. **Status Verification**: Shows final migration state

## 📋 Best Practices

### 1. Migration Development

#### ✅ DO:
- **Test migrations locally** before pushing to production
- **Use descriptive migration names** that explain what changed
- **Keep migrations small and focused** on single changes
- **Test both forward and backward migrations**
- **Use `--dry-run` flag** to preview migration changes

#### ❌ DON'T:
- **Modify existing migrations** after they've been applied to production
- **Create migrations that depend on external data**
- **Use `--fake` in production** without understanding the consequences
- **Skip migration testing** in staging environments

### 2. Production Deployment

#### ✅ DO:
- **Always backup the database** before running migrations
- **Run migrations during maintenance windows** when possible
- **Monitor migration performance** for large datasets
- **Test rollback procedures** before deployment
- **Use proper migration conflict resolution** (like our clean fix script)

#### ❌ DON'T:
- **Run migrations without backups**
- **Deploy during peak usage** without testing
- **Ignore migration warnings or errors**
- **Use manual database changes** that bypass Django migrations

### 3. Conflict Resolution

#### When Migration Conflicts Occur:

1. **Identify the root cause**:
   ```bash
   python manage.py showmigrations
   python manage.py migrate --plan
   ```

2. **Use the proper fix script**:
   ```bash
   python scripts/proper_migration_fix.py
   ```

3. **Verify the fix**:
   ```bash
   python manage.py showmigrations
   python manage.py check
   ```

### 4. Database Schema Management

#### Schema Changes:
- **Always use migrations** for schema changes
- **Test schema changes** in development first
- **Document breaking changes** in migration comments
- **Consider data migration** for complex changes

#### Data Migrations:
- **Use `RunPython` operations** for data transformations
- **Test data migrations** with production-like data
- **Handle large datasets** with batch processing
- **Provide rollback procedures** for data migrations

## 🚀 Deployment Workflow

### 1. Pre-Deployment
```bash
# Backup database
python manage.py dumpdata --natural-foreign --natural-primary > backup.json

# Check migration status
python manage.py showmigrations

# Test migrations locally
python manage.py migrate --dry-run
```

### 2. Deployment
```bash
# Run proper migration fix (if needed)
python scripts/proper_migration_fix.py

# Or run normal migrations
python manage.py migrate --noinput
```

### 3. Post-Deployment
```bash
# Verify migration status
python manage.py showmigrations

# Check for issues
python manage.py check

# Test application functionality
python manage.py test
```

## 🔍 Troubleshooting

### Common Issues:

#### 1. "Column already exists" Error
**Cause**: Database schema is out of sync with migration state
**Solution**: Use the proper migration fix script

#### 2. "Migration not found" Error
**Cause**: Migration file is missing or corrupted
**Solution**: Check migration files and restore from version control

#### 3. "Circular dependency" Error
**Cause**: Migrations have circular references
**Solution**: Restructure migrations to remove dependencies

#### 4. "Data migration failed" Error
**Cause**: Data transformation logic has errors
**Solution**: Fix the migration logic and re-run

### Debugging Commands:
```bash
# Show migration plan
python manage.py migrate --plan

# Show migration status
python manage.py showmigrations

# Check for issues
python manage.py check

# Show migration dependencies
python manage.py showmigrations --plan
```

## 📊 Monitoring

### Key Metrics to Monitor:
- **Migration execution time**
- **Database size changes**
- **Application performance** after migrations
- **Error rates** during migration

### Logging:
- **Migration start/end times**
- **Data transformation results**
- **Error messages and stack traces**
- **Performance metrics**

## 🔒 Security Considerations

### Database Access:
- **Use read-only connections** for monitoring
- **Limit migration execution** to authorized users
- **Audit migration changes** in production
- **Encrypt sensitive data** in migrations

### Backup Security:
- **Encrypt database backups**
- **Store backups securely**
- **Test backup restoration** regularly
- **Rotate backup files** appropriately

## 📚 Additional Resources

### Django Documentation:
- [Django Migrations](https://docs.djangoproject.com/en/stable/topics/migrations/)
- [Migration Operations](https://docs.djangoproject.com/en/stable/ref/migration-operations/)
- [Data Migrations](https://docs.djangoproject.com/en/stable/topics/migrations/#data-migrations)

### Tools:
- **Django Debug Toolbar**: For development debugging
- **Django Extensions**: For additional management commands
- **pgAdmin**: For PostgreSQL database management

## 🎯 Summary

The proper migration fix approach ensures:
- ✅ **Clean database state**
- ✅ **Consistent migration tracking**
- ✅ **Proper error handling**
- ✅ **Maintainable codebase**
- ✅ **Reliable deployments**

This approach eliminates the need for "hacks" and provides a solid foundation for future development.
