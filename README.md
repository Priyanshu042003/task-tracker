# task-tracker

# clone the repo 
git clone https://github.com/Priyanshu042003/task-tracker.git
cd task-tracker

# Environment Setup
#without-docker
python -m venv venv 
source venv/bin/activate 
venv\Scripts\activate 

pip install --upgrade pip
pip install -r requirements.txt 

#with-docker
docker-compose up --build -d

# Run Migrations & Collect Static Files
python manage.py migrate
python manage.py collectstatic --noinput

# Run the Development Server
#without-docker
python manage.py runserver

#with-docker
docker-compose up -d

# Start Celery Workers
#without-docker
celery -A mytask worker --loglevel=info
celery -A mytask beat --loglevel=info

#with-docker
docker-compose up -d celery_worker celery_beat

# API Testing with Postman
Import `task-tracker.postman_collection.json` into Postman to test the APIs.
