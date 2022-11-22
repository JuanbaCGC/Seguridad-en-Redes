install: 
	pip install flask flask-limiter

certificates: 
	openssl req -x509 -newkey rsa:4096 -nodes -keyout key.pem -out cert.pem -days 365
	sudo cp cert.pem /usr/local/share/ca-certificates/miservidor.local.crt
	sudo update-ca-certificates

api:
	./src/apiRest.py

tests:
	./test/test.sh

launchServer: resetServer certificates api