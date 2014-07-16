"""
Brainiac Configuration
Change this file to suit your installation's needs.
"""

enabledModules = [

]

"""
Redis config

    Specify one of the following three:

    1. host and port
     - Current values are the redis default
    2. unix_socket_path
     - The file path to the unix socket.
    3. connection_pool
      - Instance of redis.connection.ConnectionPool
"""
redis = {
    'host': 'localhost',
    'port': 6379,
    'unix_socket_path': None,
    'connection_pool': None
}


"""
Configuration for the templating system
"""
template = {
	'lookups': [
        'web/templates/'
    ],
	'modules': '/tmp/makocache/'
}