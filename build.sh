pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser --no-input
mkdir -p res/data/
wget "https://drive.usercontent.google.com/download?id=18BFdUu1fJCI6VmMnq_XLYwDvhdSBAEWw&export=download&confirm=t&uuid=2bcd0c1a-44d3-4a7f-b647-9db8ac78b40d" -O "res/data/AUD-USD.zip"
#wget "https://drive.usercontent.google.com/download?id=1f6um7gYZzq5ipv8nhKnSGu7V7TuRT2qp&export=download&confirm=t&uuid=11a76e5c-37d1-468d-a429-0127a205f8ff" -O "res/data/AUD-USD.zip"
unzip "res/data/AUD-USD.zip" -d "res/data/"

