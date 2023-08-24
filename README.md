# FAANG dcc-validate-metadata project

## Build the project

```bash
source ~/PycharmProjects/dcc-validate-metadata/venv/bin/activate
pip3 install -r requirements.txt
```

Install RabbitMQ (message broker) and Redis (in-memory data structure store) locally
```bash
brew install redis
brew install rabbitmq
```

1:
Start up rabbit-mq
```bash
rabbitmq-server
```

2:
Start up redis
```bash
redis-server
```

3:
Export KUBECONFIG to get cluster access
```bash
export KUBECONFIG = $HOME/.kube/config
```
Port-forward the elixir-jsonschema-validator-deployment to port 58853 (you can use any other available port)
```bash
kubectl port-forward deployment/elixir-jsonschema-validator-deployment 58853:3020
```

Ensure that ELIXIR_VALIDATOR_URL in the .env file is using the correct port

```bash
docker build -t dcc-validate-metadata-image --no-cache .
```
```bash
docker run -d -p 8000:8000 --name dcc-validate-metadata dcc-validate-metadata-image

docker run -it --name dcc-validate-metadata dcc-validate-metadata-image /bin/bash
```
