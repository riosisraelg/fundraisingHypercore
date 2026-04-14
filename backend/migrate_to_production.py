"""
migrate_to_production.py
========================
Migrates legacy RDS data into the new Supabase/PostgreSQL database.
This version AUTOMATICALLY creates User accounts for legacy buyers.

Handles:
1. Strips 'cancelled_at' field (removed from model)
2. Skips cancelled tickets (physically deleted in new model)
3. Groups active tickets by phone/name
4. Creates unique User accounts for each buyer with dummy credentials
5. Links tickets to those users
6. Generates 'credenciales_legacy.txt' for the admin

Usage:
    cd backend
    python manage.py migrate          # Create tables first
    python migrate_to_production.py   # Run this script
"""

import os
import sys
import json
import re
import django
from django.utils.text import slugify

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import transaction, models
from core.models import Ticket, FundraisingExtra, User

DATA_FILE = os.path.join(os.path.dirname(__file__), 'rds_data_fixed.json')
REPORT_FILE = os.path.join(os.path.dirname(__file__), 'credenciales_legacy.txt')
DEFAULT_PASSWORD = "hypercore2026"


def clean_phone(phone):
    if not phone: return ""
    return re.sub(r'[^0-9]', '', phone)[-10:]


@transaction.atomic
def migrate():
    with open(DATA_FILE) as f:
        data = json.load(f)

    tickets_data = [r for r in data if r['model'] == 'core.ticket' and r['fields']['status'] == 'active']
    print(f"📊 Total active tickets to import: {len(tickets_data)}\n")

    # Group tickets by buyer
    buyers = {}
    for t in tickets_data:
        f = t['fields']
        phone = clean_phone(f['phone'])
        name = f['full_name'].strip()
        
        # Key by phone if available, else by slugified name
        key = phone if phone else slugify(name)
        
        if key not in buyers:
            buyers[key] = {
                'name': name,
                'phone': f['phone'],
                'tickets': []
            }
        buyers[key]['tickets'].append(t)

    print(f"👥 Unique buyers identified: {len(buyers)}")
    
    report_lines = [
        "REPORTE DE CREDENCIALES - USUARIOS MIGRADOS RDS",
        "===============================================",
        f"Contraseña genérica para todos: {DEFAULT_PASSWORD}",
        "",
        f"{'NOMBRE':<35} | {'EMAIL (LOGIN)':<35} | {'TELÉFONO':<15} | {'FOLIOS'}",
        "-" * 110
    ]

    for key, info in buyers.items():
        name = info['name']
        phone = info['phone']
        
        # Generate dummy email
        # Take first name and last name
        parts = name.split()
        if len(parts) >= 2:
            email_prefix = f"{parts[0]}.{parts[1]}".lower()
        else:
            email_prefix = parts[0].lower()
            
        email_prefix = slugify(email_prefix).replace('-', '.')
        email = f"{email_prefix}@hypercore.lat"
        
        # Handle email collisions
        counter = 1
        base_email = email
        while User.objects.filter(email=email).exists():
            email = f"{email_prefix}{counter}@hypercore.lat"
            counter += 1

        # Create or Get User
        user, created = User.objects.get_or_create(
            username=email,
            defaults={
                'email': email,
                'first_name': parts[0],
                'last_name': ' '.join(parts[1:]) if len(parts) > 1 else '',
                'phone': phone
            }
        )
        if created:
            user.set_password(DEFAULT_PASSWORD)
            user.save()
            print(f"👤 Created user: {name} ({email})")
        else:
            print(f"👤 User already exists: {name}")

        folios = []
        for t_data in info['tickets']:
            pk = t_data['pk']
            fields = t_data['fields']
            
            # Handle idempotency (by PK) and collision (by Folio)
            t_obj = Ticket.objects.filter(models.Q(pk=pk) | models.Q(folio=fields['folio'])).first()
            
            if t_obj:
                print(f"   🔄 Updating {fields['folio']} — {fields['full_name']}")
                t_obj.full_name = fields['full_name']
                t_obj.phone = fields['phone']
                t_obj.status = 'active'
                t_obj.reserved_by = user
                t_obj.save()
            else:
                Ticket.objects.create(
                    id=pk,
                    folio=fields['folio'],
                    full_name=fields['full_name'],
                    phone=fields['phone'],
                    status='active',
                    created_at=fields['created_at'],
                    reserved_by=user
                )
                print(f"   ✅ Imported {fields['folio']} — {fields['full_name']}")
            
            folios.append(fields['folio'])
            
        report_lines.append(f"{name:<35} | {email:<35} | {phone:<15} | {', '.join(folios)}")

    # Fundraising Extra
    extras = [r for r in data if r['model'] == 'core.fundraisingextra']
    for record in extras:
        FundraisingExtra.objects.get_or_create(
            pk=record['pk'],
            defaults={'amount': record['fields']['amount']}
        )

    # Save report
    with open(REPORT_FILE, 'w') as f:
        f.write('\n'.join(report_lines))

    print(f"\n✅ Migration complete!")
    print(f"📄 Credentials report saved to: {REPORT_FILE}")


if __name__ == '__main__':
    migrate()
