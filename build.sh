pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser --no-input
mkdir -p res/data/
#wget "https://drive.usercontent.google.com/download?id=18BFdUu1fJCI6VmMnq_XLYwDvhdSBAEWw&export=download&confirm=t&uuid=2bcd0c1a-44d3-4a7f-b647-9db8ac78b40d" -O "res/data/AUD-USD.zip"
wget "https://drive.usercontent.google.com/download?id=1ABQDDMIZpzC6BNebzIZ3ssrxL0lo3ilw&export=download&confirm=t&uuid=9f38f336-fc3d-412c-86ba-a429f352208f" -O "res/data/AUD-USD.zip"
unzip "res/data/AUD-USD.zip" -d "res/data/"

