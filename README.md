# Perfect Home — Deploy Qo'llanma (Docker)

Quyidagi qo'llanma sizni **hozirgi holatdan boshlab** saytni **serverga chiqarish**gacha bo'lgan barcha qadamlar bilan olib boradi. Hammasi Docker orqali.

**Talablar**
1. Ubuntu server (Hetzner kabi VPS)
2. Domen bo'lsa yaxshi (ixtiyoriy, lekin production uchun tavsiya)
3. Git repo URL

**1. Serverda Docker va Git o'rnatish**
```bash
apt update
apt install -y docker.io docker-compose-plugin git
systemctl enable --now docker
```

**2. Loyihani serverga yuklash**
```bash
mkdir -p /srv/perfecthome
cd /srv/perfecthome
git clone <REPO_URL> .
```

**3. `.env` ni prodga moslash**
`.env` faylini serverda yaratamiz (localdagi `.env`ni ko'chirmang).

Secret key generatsiya:
```bash
python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(50))
PY
```

`.env` ni yozing:
```bash
cat > /srv/perfecthome/.env <<'EOF'
DJANGO_SECRET_KEY=t57StPM5nX0fNv8ejJX-IxF5bfsbTWcGngHj13_zaBrdreu3eQ8UKmSs-C-HzuKMxwY
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=116.203.192.217

DB_ENGINE=django.db.backends.postgresql
DB_NAME=perfecthome
DB_USER=perfecthome_user
DB_PASSWORD=<STRONG_DB_PASSWORD>
DB_HOST=db
DB_PORT=5432

CONTACT_ADDRESS=Tashkent, Uzbekistan
CONTACT_PHONE=+998 (00) 000-00-00
CONTACT_EMAIL=info@perfecthome.uz
CONTACT_MAP_EMBED_URL=https://www.google.com/maps
EOF
```

**4. Docker orqali ishga tushirish**
```bash
cd /srv/perfecthome
docker compose up -d --build
```

Tekshirish:
```bash
docker compose ps
docker compose logs -f web
```

**5. Superuser yaratish**
```bash
docker compose exec web python manage.py createsuperuser
```

**6. Portlarni ochish (UFW bo'lsa)**
```bash
ufw allow OpenSSH
ufw allow 80
ufw allow 443
ufw enable
```

**7. Domen sozlash (DNS)**
DNS A record:
- `@` → server IP
- `www` → server IP

**8. HTTPS (tavsiya, ixtiyoriy)**
Hozirgi konfiguratsiya HTTP (80-port). HTTPS uchun 2 yo'l:

1. Cloudflare orqali SSL yoqish  
2. Host-level reverse proxy (Nginx/Caddy) qo'shish

Agar xohlasangiz, men HTTPS uchun tayyor konfiguratsiyani qo'shib beraman.

**9. Yangi versiyani deploy qilish (update)**
```bash
cd /srv/perfecthome
git pull
docker compose up -d --build
```

**10. Foydali buyruqlar**
```bash
docker compose logs -f web
docker compose logs -f nginx
docker compose exec web python manage.py shell
docker compose exec web python manage.py migrate
```

**Izoh**
- `docker/entrypoint.sh` konteyner ishga tushganda `migrate` va `collectstatic` bajaradi.
- `staticfiles` va `media` Docker volume orqali saqlanadi.
