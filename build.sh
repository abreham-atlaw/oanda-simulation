pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser --no-input
mkdir -p res/data/
#wget "https://drive.usercontent.google.com/download?id=18BFdUu1fJCI6VmMnq_XLYwDvhdSBAEWw&export=download&confirm=t&uuid=2bcd0c1a-44d3-4a7f-b647-9db8ac78b40d" -O "res/data/AUD-USD.zip"
wget "https://drive.usercontent.google.com/download?id=1wfUT2VKIxnYlMT6F2IjzqC5dcpKegY15&export=download&authuser=0&confirm=t&uuid=2f5b82bf-0986-45b8-ba29-8d0f54134c47&at=APvzH3odnGBWv2L67xK_Iz9qvL2R:1733401722000" -O "res/data/AUD-USD.zip"
unzip "res/data/AUD-USD.zip" -d "res/data/"
