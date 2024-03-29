pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser --no-input
wget "https://www.dropbox.com/scl/fi/m3gjmbvif1fz3vg5bz9lm/AUD-USD.csv?rlkey=piod5flcvreghuoa7k3plfp5n&dl=0&raw=1" -O "res/data/AUD-USD-downloaded.csv"
