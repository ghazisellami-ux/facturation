import sys
sys.path.insert(0, '.')
from app.models import user, company, client, invoice, supplier
from app.database import SessionLocal
from app.utils.auth import hash_password, verify_password

db = SessionLocal()
u = db.query(user.User).filter(user.User.email == 'ghazi.sellami@gmail.com').first()
if u:
    new_pass = 'Sic2024'
    u.password_hash = hash_password(new_pass)
    db.commit()
    # Verify it works
    ok = verify_password(new_pass, u.password_hash)
    print(f'Password reset to: {new_pass}')
    print(f'Verify OK: {ok}')
else:
    print('User not found')
