# flowerconfig.py
# from kombu import serialization
#
# def enable_insecure_serializers():
#     serialization.enable_insecure_serializers()
#
# enable_insecure_serializers()

# Flower configuration
address = '0.0.0.0'  # Listen on all interfaces
port = 5555



# Celery settings matching worker configuration
# NOTE: accept content currently not working for pickle
task_serializer = 'json'
result_serializer = 'json'
event_serializer = 'json'
accept_content = ['application/json', 'application/x-python-serialize']
result_accept_content = ['application/json', 'application/x-python-serialize']
