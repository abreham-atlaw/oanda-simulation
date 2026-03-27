pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser --no-input
mkdir -p res/data/
wget "https://drive.usercontent.google.com/download?id=1J17NVN6iY4XqoDThthT4eUB0ack5XrK6&export=download&authuser=0&confirm=t&uuid=2f5b82bf-0986-45b8-ba29-8d0f54134c47&at=APvzH3odnGBWv2L67xK_Iz9qvL2R:1733401722000" -O "res/data/data.zip"
unzip "res/data/data.zip" -d "res/data/"
