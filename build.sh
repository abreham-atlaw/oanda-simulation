pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser --no-input
mkdir -p res/data/
wget "https://drive.usercontent.google.com/download?id=1lp6oNYQ7K0rfsPDWDoY1-DyqkgNJeJzA&export=download&authuser=0&confirm=t&uuid=2f5b82bf-0986-45b8-ba29-8d0f54134c47&at=APvzH3odnGBWv2L67xK_Iz9qvL2R:1733401722000" -O "res/data/ZAR-USD.zip"
unzip "res/data/ZAR-USD.zip" -d "res/data/"
