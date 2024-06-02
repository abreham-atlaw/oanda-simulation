pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser --no-input
mkdir -p res/data/
wget "https://docs.google.com/uc?export=download&id=1p48nXH5mJCkvomN2MtumacSrjnFxKLHq" -O "res/data/AUD-USD-downloaded.csv"
