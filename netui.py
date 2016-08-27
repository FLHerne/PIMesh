from urllib.parse import quote, unquote, parse_qs

from jinja2 import Environment, FileSystemLoader

from network import Network

filename = 'network0.pimesh'

with open(filename) as net_file:
    net = Network.from_file(net_file)

jinja_env = Environment(loader=FileSystemLoader('./html'),
                        extensions=['jinja2.ext.autoescape'],
                        autoescape=True)

tpl_list = jinja_env.get_template('list.html')
tpl_view = jinja_env.get_template('view.html')

def application(env, start_response):

    path = env.get('PATH_INFO', "").lstrip('/')
    cmd, *rest = path.split("/", 1)
    arg = unquote(rest[0]).strip() if rest else ""

    try:
        request_body_size = int(env.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0
    request_body = env['wsgi.input'].read(request_body_size).decode()

    status = "200 OK"
    headers = [('Content-Type','text/html')]

    if path == "plain":
        headers = [
            ('Content-Type','text/plain'),
            ('Content-Disposition', 'attachment; filename="%s"' %(filename))
        ]
        with open(filename) as net_file:
            body = net_file.read()

    elif cmd == "list" and env['REQUEST_METHOD'] == 'POST':
        try:
            view_entity = parse_qs(request_body)['view'][0]
            new_url = '/view/%s' %quote(view_entity)
        except:
            new_url = '/list'
        status = "303 See Other"
        headers.append(('Location', new_url))
        body = '<a href="%s">Redirect</a>' %new_url

    elif cmd == "view" and arg and env['REQUEST_METHOD'] == 'POST':
        try:
            request_dict = parse_qs(request_body)
            tag = request_dict['tag'][0].strip()
            target = request_dict['target'][0].strip()
            inverse_tag = request_dict.get('inverse_tag', [""])[0].strip()
            if not inverse_tag:
                inverse_tag = Network.reciprocal(tag)
            if not all((tag, target, inverse_tag)):
                raise ValueError()
            net.addlink(arg, tag, target, inverse_tag)
            status = "200 OK"
        except:
            status = "400 Bad Request"
        body = tpl_view.render(name=arg, links=net[arg])

    elif cmd == "view" and arg:
        body = tpl_view.render(name=arg, links=net[arg])

    elif path == "list":
        body = tpl_list.render(entities=net.origin_counts())

    elif not path:
        status = "301 Moved Permanently"
        headers.append(('Location', '/list'))
        body = body = '<a href="/list">Redirect</a>'

    else:
        status = "404 Not Found"
        body = "No such place!"

    start_response(status, headers)
    return [bytes(body, 'UTF-8')]
