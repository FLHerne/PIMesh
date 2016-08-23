from urllib.parse import quote, unquote

from jinja2 import Environment, FileSystemLoader

from network import Network

filename = 'network0.pimesh'

with open(filename) as net_file:
    network = Network.from_file(net_file)

jinja_env = Environment(loader=FileSystemLoader('./html'),
                        extensions=['jinja2.ext.autoescape'],
                        autoescape=True)

tpl_list = jinja_env.get_template('list.html')
tpl_view = jinja_env.get_template('view.html')

def application(env, start_response):

    status = "200 OK"
    headers = [('Content-Type','text/html')]
    body = ""

    path = env.get('PATH_INFO', "").lstrip('/')
    cmd, *rest = path.split("/", 1)
    arg = unquote(rest[0]).strip() if rest else ""

    if path == "plain":
        headers = [
            ('Content-Type','text/plain'),
            ('Content-Disposition', 'attachment; filename="%s"' %(filename))
        ]
        with open(filename) as net_file:
            body = net_file.read()
    elif cmd == "view" and arg:
        body = tpl_view.render(name=arg, links=network[arg])
    else:
        body = tpl_list.render(entities=network.origin_counts())

    start_response(status, headers)
    return [bytes(body, 'UTF-8')]
