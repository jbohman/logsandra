import yaml

def parse(config_file):
    file_handler = open(config_file)
    config = yaml.load(file_handler.read())

    if 'ident' not in config:
        import socket
        ident = socket.gethostname()
        if not ident:
            raise Exception('Config %s must contain an ident' % config_file)
        else:
            config['ident'] = ident

    if 'httpd_address' not in config:
        config['httpd_address'] = '0.0.0.0'

    if 'httpd_port' not in config: 
        config['httpd_port'] = 5000

    if 'httpd_config' not in config:
        config['httpd_config'] = 'development.ini'


    if 'cassandra_address' not in config:
        config['cassandra_address'] = 'localhost'

    if 'cassandra_port' not in config:
        config['cassandra_port'] = '9160'

    if 'cassandra_timeout' not in config:
        config['cassandra_timeout'] = '5'

    return config
