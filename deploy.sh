#! /bin/bash

## build docker image and tag it
echo " ==> Building docker image"
docker build -t vinaykumar6/vinay-devops-test .

## login to docker hub
## Username and password not mentioned , fetched from Windows credential manager in my case
echo " ==> Before docker login"
docker login

# push image to docker hub repository
echo " ==> push image to docker hub"
docker push vinaykumar6/vinay-devops-test

## k8s will pull image form docker hub and deploy application
echo " ==> Apply k8s yaml file to the cluster"
if [[ $(kubectl apply -f k8s | grep -c 'deployment unchanged') == 1 ]]; then
    echo " ==> Patching deployment to pull latest image from docker hub"
    kubectl rollout restart deployment mypython-app-rest-deployment -n devops-test
    echo " ==> success"
else
    echo " ==> k8s objects created. deployment patch not required"
fi