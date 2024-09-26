pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser --no-input
mkdir -p res/data/
#wget "https://drive.usercontent.google.com/download?id=18BFdUu1fJCI6VmMnq_XLYwDvhdSBAEWw&export=download&confirm=t&uuid=2bcd0c1a-44d3-4a7f-b647-9db8ac78b40d" -O "res/data/AUD-USD.zip"
wget "https://drive.usercontent.google.com/download?id=1pgwQBoCFKCNDu5teR_DEQE0TPrUnmxly&export=download&authuser=0&confirm=t&uuid=853a604c-983e-4276-a0ab-26106b637f63&at=AN_67v0AJRo1LDn5N7qhwzps2X0d%3A1727326916450" -O "res/data/AUD-USD.zip"
unzip "res/data/AUD-USD.zip" -d "res/data/"

