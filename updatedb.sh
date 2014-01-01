rm book.db
python manage.py syncdb
python manage.py loaddata $1