import sys
sys.path.insert(0, '.')

# Import ALL models to resolve relationships
from app.models import user, company, client, invoice, supplier
from app.database import SessionLocal
from app.utils.auth import hash_password

db = SessionLocal()
u = user.User(
    email='ghazi.sellami@gmail.com',
    password_hash=hash_password('SicFacture2024!'),
    first_name='Ghazi',
    last_name='Sellami',
    phone='+21652770830'
)
db.add(u)
db.flush()
c = company.Company(
    name='Sellami Ingenierie et consulting',
    owner_id=u.id,
    email='ghazi.sellami@gmail.com',
    phone='+21652770830'
)
db.add(c)
db.commit()
print(f'OK: User created - email: ghazi.sellami@gmail.com')
