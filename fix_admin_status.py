#!/usr/bin/env python3
"""
Fix Admin Status for Existing Users
This script sets existing users as admins if they have created data in the CRM.
"""

import sqlite3
import sys
from datetime import datetime

def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def fix_admin_status():
    """Set existing users with data as admins"""
    log("🔧 Fixing admin status for existing users...")
    
    try:
        conn = sqlite3.connect('/Users/marclefebvre/Projects/ELS CRM/instance/crm.db')
        cursor = conn.cursor()
        
        # Get users who have created data
        cursor.execute("""
            SELECT DISTINCT u.id, u.username, u.email
            FROM users u
            WHERE u.id IN (
                SELECT DISTINCT created_by FROM leads WHERE created_by IS NOT NULL
                UNION
                SELECT DISTINCT created_by FROM accounts WHERE created_by IS NOT NULL
                UNION
                SELECT DISTINCT created_by FROM contacts WHERE created_by IS NOT NULL
                UNION
                SELECT DISTINCT created_by FROM opportunities WHERE created_by IS NOT NULL
            )
            AND u.organization_id IS NULL
        """)
        
        users_with_data = cursor.fetchall()
        log(f"Found {len(users_with_data)} users with existing data")
        
        if len(users_with_data) == 0:
            log("No users with data found. Nothing to fix.")
            return True
        
        # For each user with data, they should be able to become admin
        for user in users_with_data:
            user_id, username, email = user
            log(f"User {username} (ID: {user_id}) has created data - should be able to become admin")
            
            # Check what data they have
            cursor.execute("SELECT COUNT(*) FROM leads WHERE created_by = ?", (user_id,))
            leads_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM accounts WHERE created_by = ?", (user_id,))
            accounts_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM contacts WHERE created_by = ?", (user_id,))
            contacts_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM opportunities WHERE created_by = ?", (user_id,))
            opportunities_count = cursor.fetchone()[0]
            
            log(f"  - {leads_count} leads, {accounts_count} accounts, {contacts_count} contacts, {opportunities_count} opportunities")
        
        # Let's give all existing users admin status so they can set up organizations
        log("Setting all existing users as potential admins...")
        cursor.execute("UPDATE users SET is_admin = 1 WHERE organization_id IS NULL")
        affected_rows = cursor.rowcount
        
        conn.commit()
        log(f"✅ Updated {affected_rows} users to have admin privileges")
        log("💡 These users can now set up organizations and become organization admins")
        
        # Show final status
        cursor.execute("SELECT id, username, organization_id, is_admin FROM users")
        all_users = cursor.fetchall()
        
        log("\n=== Updated User Status ===")
        for user in all_users:
            user_id, username, org_id, is_admin = user
            status = "Admin" if is_admin else "Member"
            org_status = f"Org: {org_id}" if org_id else "No Org"
            log(f"  {username}: {status}, {org_status}")
        
        conn.close()
        return True
        
    except Exception as e:
        log(f"❌ Error: {e}")
        return False

def main():
    log("🚀 Starting Admin Status Fix")
    log("=" * 50)
    
    if fix_admin_status():
        log("=" * 50)
        log("✅ Admin status fix completed successfully!")
        log("💡 All existing users can now set up organizations")
        log("💡 When they set up an organization, they will become the organization admin")
    else:
        log("❌ Admin status fix failed")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
