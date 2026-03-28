# Perfect Home

`Perfect Home` Django loyihasi Docker orqali ishga tushadi. Hozirgi stack:

- `web` - Django + Gunicorn
- `db` - PostgreSQL 16
- `nginx` - reverse proxy va static/media uchun

Quyidagi deploy jarayoni Docker va Docker Compose ishlaydigan istalgan Linux server, VPS yoki cloud VM uchun mos. Bu qo'llanma providerga bog'liq emas.

## 1. Talablar

Serverda quyidagilar bo'lishi kerak:

- Docker
- Docker Compose plugin
- Git
- 80-port ochiq bo'lishi kerak
- HTTPS ishlatmoqchi bo'lsangiz 443-port ham ochiq bo'lishi kerak

Ubuntu yoki Debian uchun misol:

```bash
apt update
apt install -y docker.io docker-compose-plugin git
systemctl enable --now docker
```

Agar boshqa distributiv ishlatsangiz, shu paketlarning ekvivalentini o'rnating.

## 2. Loyihani serverga yuklash

```bash
mkdir -p /srv/perfecthome
cd /srv/perfecthome
git clone <REPO_URL> .
```

## 3. Environment faylni tayyorlash

Repo ichida `.env.example` bor. Serverda undan nusxa oling:

```bash
cd /srv/perfecthome
cp .env.example .env
```

Yangi secret key generatsiya qiling:

```bash
python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(50))
PY
```

Keyin `.env` faylni tahrir qiling:

```bash
nano .env
```

Muhim qiymatlar:

- `DJANGO_SECRET_KEY` - yangi tasodifiy qiymat bo'lishi kerak
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS` - domen va kerak bo'lsa server IP
- `DJANGO_CSRF_TRUSTED_ORIGINS` - `https://domeningiz` ko'rinishida
- `DB_HOST=db` - agar compose ichidagi PostgreSQL ishlatilsa
- `DB_PASSWORD` - kuchli parol bo'lishi kerak

## 4. Birinchi deploy

```bash
cd /srv/perfecthome
docker compose up -d --build
```

Tekshirish:

```bash
docker compose ps
docker compose logs -f web
docker compose logs -f nginx
```

Izoh:

- `docker/entrypoint.sh` konteyner ishga tushganda `migrate` va `collectstatic` bajaradi
- PostgreSQL ma'lumotlari `postgres_data` volume ichida saqlanadi
- static fayllar `static` volume ichida saqlanadi
- media fayllar `media` volume ichida saqlanadi

## 5. Admin foydalanuvchi yaratish

```bash
docker compose exec web python manage.py createsuperuser
```

## 6. Domen ulash

DNS tomonida quyidagilarni ulang:

- `@` -> server IP
- `www` -> server IP

Keyin `.env` ichida `DJANGO_ALLOWED_HOSTS` va `DJANGO_CSRF_TRUSTED_ORIGINS` ni domen bilan yangilang.

Misol:

```env
DJANGO_ALLOWED_HOSTS=example.com,www.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com
```

## 7. HTTPS

Hozirgi compose konfiguratsiya HTTP orqali ishlaydi. HTTPS uchun 3 ta odatiy yo'l bor:

1. Server oldiga host-level Nginx yoki Caddy qo'yish
2. Cloudflare proxy va SSL ishlatish
3. Alohida reverse proxy stack ishlatish

Qaysi variantni tanlamang, ilovaga kelayotgan domenlar `.env` ichida yozilgan bo'lishi kerak.

## 8. Yangilash deployi

Kod yangilanganda:

```bash
cd /srv/perfecthome
git pull
docker compose up -d --build
```

Kerak bo'lsa eski image'larni tozalash:

```bash
docker image prune -f
```

## 9. Foydali buyruqlar

```bash
docker compose ps
docker compose logs -f web
docker compose logs -f nginx
docker compose logs -f db
docker compose exec web python manage.py shell
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput
docker compose exec db sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

## 10. Backup tavsiyasi

Database backup:

```bash
docker compose exec -T db sh -lc 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > backup.sql
```

Media backup:

1. `docker volume ls` bilan media volume nomini toping
2. Shu volume'ni alohida backup qiling yoki server snapshot ishlating

## 11. Mavjud media fayllarni ko'chirish

Agar sizda oldindan tayyor `media/` papka bo'lsa va uni yangi serverga ko'chirmoqchi bo'lsangiz:

1. Avval `docker compose up -d --build` ni ishga tushiring
2. Media volume nomini toping:

```bash
docker volume ls | grep media
```

3. Fayllarni volume ichiga ko'chiring:

```bash
docker run --rm \
  -v <MEDIA_VOLUME>:/to \
  -v "$PWD/media:/from:ro" \
  alpine sh -c 'cp -av /from/. /to/'
```

`<MEDIA_VOLUME>` o'rniga real volume nomini yozing.

## 12. Muammolarni tekshirish

Agar sayt ochilmasa, odatda sabablari shular bo'ladi:

- `DJANGO_ALLOWED_HOSTS` noto'g'ri
- `DJANGO_CSRF_TRUSTED_ORIGINS` bo'sh yoki noto'g'ri
- `DB_HOST` noto'g'ri berilgan
- firewall 80 yoki 443 portni yopib turibdi
- domen hali server IP'ga ulanmagan

## 13. Muhim eslatma

- `.env` ni git'ga qo'shmang
- production serverda `DJANGO_DEBUG=False` bo'lsin
- secret key va database parolini haqiqiy xavfsiz qiymatlarga almashtiring
- agar tashqi PostgreSQL ishlatsangiz, `.env` ichida `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` ni o'sha server qiymatlariga almashtiring
