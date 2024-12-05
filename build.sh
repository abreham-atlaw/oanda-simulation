pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser --no-input
mkdir -p res/data/
#wget "https://drive.usercontent.google.com/download?id=18BFdUu1fJCI6VmMnq_XLYwDvhdSBAEWw&export=download&confirm=t&uuid=2bcd0c1a-44d3-4a7f-b647-9db8ac78b40d" -O "res/data/AUD-USD.zip"
wget "https://drive.usercontent.google.com/download?id=1ESNs_a0pFmcsTE7IZPGTPMpWgUvRHj3J&export=download&authuser=0&confirm=t&uuid=969acda4-c044-4633-ae86-94eec0885914&at=APvzH3qFKnTpneB2GjVHpqeLXfqs:1733401220616" -O "res/data/AUD-USD.zip"
unzip "res/data/AUD-USD.zip" -d "res/data/"
