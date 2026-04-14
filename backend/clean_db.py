"""
clean_db.py
===========
Utility to wipe all test data from the database while preserving Admin accounts.

Deletes:
- All Tickets
- All Draw Results
- All Withdraws
- All Fundraising Extras
- All Users EXCEPT those with is_staff=True or is_superuser=True

Usage:
    cd backend
    python clean_db.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from core.models import Ticket, DrawResult, Withdraw, FundraisingExtra, User
from django.db import transaction

@transaction.atomic
def clean():
    print("🧹 Starting database cleanup...")
    
    # Delete related raffle data
    t_count = Ticket.objects.all().count()
    Ticket.objects.all().delete()
    print(f"   🗑️  Deleted {t_count} tickets")
    
    dr_count = DrawResult.objects.all().count()
    DrawResult.objects.all().delete()
    print(f"   🗑️  Deleted {dr_count} draw results")
    
    w_count = Withdraw.objects.all().count()
    Withdraw.objects.all().delete()
    print(f"   🗑️  Deleted {w_count} withdraws")
    
    fe_count = FundraisingExtra.objects.all().count()
    FundraisingExtra.objects.all().delete()
    print(f"   🗑️  Deleted {fe_count} fundraising extra records")
    
    # Delete non-admin users
    u_count = User.objects.filter(is_staff=False, is_superuser=False).count()
    User.objects.filter(is_staff=False, is_superuser=False).delete()
    print(f"   🗑️  Deleted {u_count} non-staff users")
    
    print("\n✅ Database is now clean (Admins preserved). Ready for production import.")

if __name__ == '__main__':
    confirm = input("⚠️  WARNING: This will delete ALL ticket and user data (except admins). Type 'YES' to proceed: ")
    if confirm == 'YES':
        clean()
    else:
        print("❌ Cleanup cancelled.")
