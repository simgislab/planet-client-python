import click
import json
from planet import api

client = api.Client()

pretty = click.option('-pp', '--pretty', default=False, is_flag=True)
scene_type = click.option('-s', '--scene-type', default='ortho')


def check(func, *args, **kw):
    try:
        return func(*args, **kw)
    except api.APIException, ex:
        msg = "%s: %s" % (type(ex).__name__, ex.message)
        raise click.ClickException(msg)


@click.group()
@click.option('-k', '--api-key',
              help='Valid API key - or via env variable %s' % api.ENV_KEY)
@click.option('-u', '--base-url', help='Optional for testing')
def cli(api_key, base_url):
    '''Planet API Client'''
    if api_key:
        client.api_key = api_key
    if base_url:
        client.base_url = base_url


@cli.command()
def list_all_scene_types():
    '''List all scene types.'''
    click.echo(check(client.list_all_scene_types))


@scene_type
@click.argument('id', nargs=-1)
@click.option('--product-type', default=None)
@cli.command()
def fetch_scene_geotiff(id, scene_type, product_type):
    '''Fetch full scene image(s)'''
    for i in id:
        img = check(client.fetch_scene_geotiff, i, scene_type, product_type)
        click.echo('fetching %s' % img.name)
        with click.progressbar(length=img.size) as bar:
            callback = lambda n: bar.update(n)
            img.write(callback=callback)


@scene_type
@click.argument("scene-ids", nargs=-1)
@click.option('--product-type', default=None)
@cli.command('thumbnails')
def fetch_scene_thumbnail(scene_ids, scene_type, product_type):
    '''Fetch scene thumbnail(s)'''
    
    if len(scene_ids) == 0:
        scene_ids = map(lambda s: s.strip(), click.open_file('-').readlines())
    
    for i in scene_ids:
        img = check(client.fetch_scene_thumbnail, i, scene_type, product_type)
        click.echo('fetching %s' % img.name)
        img.write()


@pretty
@scene_type
@click.argument('id', nargs=1)
@cli.command()
def fetch_scene_info(id, scene_type, pretty):
    '''Fetch scene metadata'''
    res = check(client.fetch_scene_info, id, scene_type)
    if pretty:
        res = json.dumps(json.loads(res), indent=2)
    click.echo(res)


@pretty
@scene_type
@cli.command('get-scenes-list')
@click.argument("aoi", default="-", required=False)
def get_scenes_list(scene_type, pretty, aoi):
    '''Get a list of scenes'''
    
    if aoi == "-":
        src = click.open_file('-')
        if not src.isatty():
            lines = src.readlines()
            aoi = ''.join([ line.strip() for line in lines ])
    
    
    res = client.get_scenes_list(scene_type=scene_type, intersects=aoi)
    if pretty:
        res = json.dumps(json.loads(res), indent=2)
    click.echo(res)