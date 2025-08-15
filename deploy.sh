
echo "Building Docker images..."

docker build -t standup-server:latest ./server
docker build -t standup-frontend:latest ./frontend

docker build -t standup-scheduler:latest ./schedular

echo "Loading images into Kubernetes..."
docker save standup-server:latest | docker exec -i docker-desktop ctr -n=k8s.io images import -
docker save standup-frontend:latest | docker exec -i docker-desktop ctr -n=k8s.io images import -
docker save standup-scheduler:latest | docker exec -i docker-desktop ctr -n=k8s.io images import -

echo "Applying Kubernetes configurations..."

kubectl apply -f k8s/configmap.yaml

if [ ! -f "k8s/secrets.yaml" ] || grep -q "<base64-encoded" k8s/secrets.yaml; then
    echo "⚠️  Warning: Please update k8s/secrets.yaml with your actual base64-encoded values:"
    echo "   echo -n 'your-slack-client-id' | base64"
    echo "   echo -n 'your-slack-client-secret' | base64"
    echo "   echo -n 'your-slack-signing-secret' | base64"
    echo "   echo -n 'your-openai-api-key' | base64"
    echo ""
    echo "Then run: kubectl apply -f k8s/secrets.yaml"
else
    kubectl apply -f k8s/secrets.yaml
fi

kubectl apply -f k8s/mongodb-deployment.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/server-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/scheduler-deployment.yaml

echo "Deployment completed!"
echo "Check status with: kubectl get pods"
echo "Access frontend: kubectl port-forward service/standup-frontend 3000:3000"
echo "Access backend: kubectl port-forward service/standup-server 4000:4000"
