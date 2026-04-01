import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Ticket
from core.ticket_generator import generate_ticket_pdf
from django.contrib.auth.models import User

user, _ = User.objects.get_or_create(username='test_user')
ticket, _ = Ticket.objects.get_or_create(folio="HC-999", full_name="Test Buyer", phone="12345678", created_by=user)

pdf_bytes = generate_ticket_pdf(ticket, "http://localhost:8000")
with open('test_ticket.pdf', 'wb') as f:
    f.write(pdf_bytes)
print("PDF generated successfully.")
