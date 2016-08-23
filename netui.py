from urllib.parse import quote, unquote

from jinja2 import Environment, FileSystemLoader

from network import Network

with open('network0.pimesh') as net_file:
    network = Network.from_file(net_file)

jinja_env = Environment(loader=FileSystemLoader('./html'),
                        extensions=['jinja2.ext.autoescape'],
                        autoescape=False)

tpl_list = jinja_env.get_template('list.html')
tpl_view = jinja_env.get_template('view.html')

def application(env, start_response):
    start_response('200 OK', [('Content-Type','text/html')])

    output = ""
    path = env.get('PATH_INFO', "").lstrip('/')
    cmd, *rest = path.split("/", 1)
    arg = unquote(rest[0]).strip() if rest else ""

    print("A", cmd, "B", arg)
    if cmd == "view" and arg:
        output = tpl_view.render(name=arg, links=network[arg])
    else:
        output = tpl_list.render(entities=network.origin_counts())
    return [bytes(output, 'UTF-8')]
