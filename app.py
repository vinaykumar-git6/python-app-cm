from flask import Flask,jsonify,request,render_template,Response
from kubernetes import client, config
from kubernetes.client import ApiClient
from kubernetes.client.rest import ApiException
import logging
import json
import os

## assign a unique name to flask app
app = Flask(__name__)

## port number to be read from ENV variable. This is injected at container runtime from config map in EKS namespace.
port = int(os.getenv("SERVE_PORT"))

## Riase exception in case port number is not present in environment variable.
if not port:
    raise ValueError("No SERVE_PORT set for Flask application")

## GET /healthz for health check. this is for pod Liveness probe configuration in deployment.yaml
@app.route('/healthz')
def health_check():
    return {'message': 'healthy'}, 200


## POST	/configs
## endpoint to create config map, namespace is coming as input JSON request.
## namespace being used is default for this test.
@app.route('/configs', methods=['POST'])
def create_config():
    request_data=request.get_json()
    config.load_incluster_config()
    api_instance = client.CoreV1Api()
    cmap = client.V1ConfigMap()
    cmap.metadata = client.V1ObjectMeta(name=request_data['name'])
    cmap.data = {}
    for key, value in request_data['metadata'].items():
        logging.info("Creating config map with key = {key}, and value = {value}".format(key=key, b=4, value=value))
        cmap.data[key] = value
    try:
        api_response= api_instance.create_namespaced_config_map(namespace=request_data['namespace'], body=cmap)
        logging.info("api_response : {api_response}".format(api_response=api_response))
        return {'message': 'config map created'}, 200
    except ApiException as e:
        logging.info("Exception when calling CoreV1Api->read_namespaced_config_map : {e}".format(e=e))
        return {'error' : 'config map already exists'}, 409

## GET	/configs
## Endpoint to get config map. config map name is passed as path parameter,
## Retrieve config map from default namespace for this test.
@app.route('/configs/<string:cmap_name>')
def get_config(cmap_name):
    request_data=request.get_json()
    config.load_incluster_config()
    api_instance = client.CoreV1Api() 
    namespace = 'default'
    try: 
        api_response = api_instance.read_namespaced_config_map(name=cmap_name, namespace='default')
        logging.info("api_response : {api_response}".format(api_response=api_response))
        #return jsonify(api_response.data), 200
        rs=ApiClient().sanitize_for_serialization(api_response)
        return Response(json.dumps(rs), mimetype='application/json', status=200)
    except ApiException as e:
        logging.info("Exception when calling CoreV1Api->read_namespaced_config_map : {e}".format(e=e))
        return {'error' : 'config map not found'}, 404

## GET	/configs
## Endpoint to List all config map from default namespace for this test.
@app.route('/configs')
def get_config_all():
    request_data=request.get_json()
    config.load_incluster_config()
    api_instance = client.CoreV1Api() 
    namespace = 'default'
    try: 
        api_response = api_instance.list_namespaced_config_map('default')
        logging.info("api_response : {api_response}".format(api_response=api_response))
        rs=ApiClient().sanitize_for_serialization(api_response)
        return Response(json.dumps(rs), mimetype='application/json', status=200)
    except ApiException as e:
        logging.info("Exception when calling CoreV1Api->list_namespaced_config_map : {e}".format(e=e))
        return {'error' : 'config map not found'}, 404
        
## DELETE	/configs/{name}
## Endpoint to delete config map from default namespace for this test.
## configmap name to be passed as path parameter
## body is empty JSON :  {}
@app.route('/configs/<string:cmap_name>', methods=['DELETE'])
def delete_config(cmap_name):
    request_data=request.get_json()
    config.load_incluster_config()
    api_instance = client.CoreV1Api() 
    namespace = 'default'
    try: 
        api_response = api_instance.delete_namespaced_config_map(name=cmap_name, body={}, namespace=namespace)
        logging.info("api_response : {api_response}".format(api_response=api_response))
        return {'message' : 'config map deleted succcessfully'}, 204
    except ApiException as e:
        logging.info("Exception when calling CoreV1Api->delete_namespaced_config_map : {e}".format(e=e))
        return {'error' : 'config map not found'}, 404

## PUT/PATCH	/configs/{name}
## Endpoint to update config map in default namespace for this test.
## configmap name to be passed as path parameter
## JSON body will contain the key to be updated
@app.route('/configs/<string:cmap_name>', methods=['PATCH'])
def patch_config(cmap_name):
    request_data=request.get_json()
    config.load_incluster_config()
    api_instance = client.CoreV1Api()
    cmap = client.V1ConfigMap()
    cmap.metadata = client.V1ObjectMeta(name=cmap_name)
    cmap.data = {}
    for key, value in request_data['metadata'].items():
        cmap.data[key] = value
    namespace = 'default'
    try: 
        api_response =api_instance.patch_namespaced_config_map(name=cmap_name, body=cmap, namespace='default')
        logging.info("api_response : {api_response}".format(api_response=api_response))
        return {'message' : 'config map updated succcessfully'}, 200
    except ApiException as e:
        logging.info("Exception when calling CoreV1Api->delete_namespaced_config_map : {e}".format(e=e))
        return {'error' : 'config map not found'}, 404

## GET	/search?metadata.key=value
## Search config map based on metaddata field in config map
## search param to be passed as Query param.
@app.route('/config-service/search')
def search_query_config():
    id = request.args.get('metadata')
    config.load_incluster_config()
    api_instance = client.CoreV1Api()
    try: 
        api_response = api_instance.list_namespaced_config_map('default', field_selector='metadata.name={id}'.format(id=id))
        logging.info("api_response : {api_response}".format(api_response=api_response))
        rs=ApiClient().sanitize_for_serialization(api_response)
        return Response(json.dumps(rs), mimetype='application/json', status=200)
    except ApiException as e:
        logging.info("Exception when calling CoreV1Api->delete_namespaced_config_map : {e}".format(e=e))
        return {'error' : 'config map not found'}, 404

## run app on the specified port number
app.run(debug=True,host='0.0.0.0',port=port)