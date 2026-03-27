web: sh -c "python manage.py migrate --noinput && python manage.py ensure_superuser && gunicorn worldserver.wsgi:application --bind 0.0.0.0:$PORT"
release: sh -c "python manage.py collectstatic --noinput && python manage.py migrate --noinput && python manage.py ensure_superuser"
