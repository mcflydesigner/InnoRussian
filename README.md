# InnoRussian
It is a Django webapp for foreign students to live in Russia. It's just a pocket dictionary which can help you. 

# Deploying the project
The project is deployed on [Heroku](https://murmuring-lowlands-42299.herokuapp.com/): https://murmuring-lowlands-42299.herokuapp.com/
## 1. install python 3.9
A good tutorial is available [here](https://linuxize.com/post/how-to-install-python-3-9-on-ubuntu-20-04/)
## 2. Clone the project
```
git clone https://github.com/mcflydesigner/InnoRussian.git
```
## 3. Setup the DB and SMTP Mail Server
In the file *djangoIR/settings.py* change ***DATABASES*** and ***EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_PORT***.
## 4. Run the migrations
Move to the main directory of the project, and in the shell run the following commands
```
python manage.py makemigrations
```
```
python manage.py migrate
```
## 5. Finally, run the server
```
python manage.py runserver
```

And enjoy :)
