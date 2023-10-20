import json
import logging
import requests
from flask import make_response
from datetime import date
from urllib.parse import urlunsplit, urlparse
from humanfriendly import format_size
from ckan.model import Session, Resource
from ckan.common import config

log = logging.getLogger(__name__)

UPDATE_FREQS = {
    '-1': u'Publicación única',
    '0': 'Enlace externo',
    '1': 'Diario',
    '7': 'Semanal',
    '15': 'Quincenal',
    '30': 'Mensual',
    '60': 'Bimestral',
    '90': 'Trimestral',
    '182': 'Semestral',
    '365': 'Anual',
    '1826': 'Quinquenal'
}


def inc_counter(counter, key, subkey, val=1):
    """
    Increments in val the value of counter[key][subkey]
    """
    if key not in counter:
        counter[key] = {}
    counter[key].update([(subkey, counter[key].get(subkey, 0) + val)])


def test_link_head(uri, **kwargs):
    r = requests.head(uri, **kwargs)
    if not r.ok:
        # try with allow_redirects:
        r = requests.head(uri, allow_redirects=True, **kwargs)
    return r


def test_link_body(uri, **kwargs):
    r = requests.get(uri, **kwargs)
    return r


def link_health(url, config, return_size=False):
    # use an auxiliar variable uri to test acording the environment
    o = urlparse(url)
    print(u'Checking link health: %s' % url)
    io = urlparse(config.get('ckan.internal_site_url', 'http://localhost:5000'))
    proxies = {
        'http': config.get('http_proxy', None),
        'https': config.get('https_proxy', None)
    }

    uri = url

    # some servers dont like the default user agent, so we change it
    timeout, headers = 2, {'User-Agent': 'Mozilla/5.0'}
    try:
        r = None
        try:
            r = test_link_head(uri, timeout=timeout, proxies=proxies, headers=headers)
            if r.status_code == 405:
                raise requests.ConnectionError()
        except requests.exceptions.SSLError:
            r = test_link_head(uri, timeout=timeout, proxies=proxies, headers=headers, verify=False)
        except requests.ConnectionError:
            # some servers block head verb, so we use a get but only to check
            # the content and not download it, but we must close the resource
            headers["Range"] = "bytes=0-100"
            r = test_link_body(uri, stream=True, timeout=timeout, proxies=proxies, headers=headers)
        finally:
            ok = r.ok
            r.close()
            assert ok
            if return_size:
                res_size = int(r.headers.get('Content-Length', r.headers.get('Content-Range').split('/')[1]))
                return ('ok', format_size(res_size))
    except AssertionError:
        res_status = u'enlace roto %s' % r.status_code
        return (res_status, None) if return_size else res_status
    except Exception as e:
        print('Failed to check link health: %s' % e)
        res_status = u'enlace roto %s' % e.__class__.__name__
        return (res_status, None) if return_size else res_status


def resource_health(resource_id, include_status=True):
    r = Session.query(Resource).get(resource_id)
    if r.url.startswith('http'):
        url = r.url
    else:
        url = u'%s/dataset/%s/resource/%s/download/%s' % (config.get('ckan.site_url'), r.package_id, r.id, r.url)
    res_health = link_health(url, config) or u'ok'
    log.info('Checking URL health {}'.format(url))
    if include_status:
        response = make_response()
        response.headers['Content-Type'] = 'application/json'
        response.data = json.dumps((res_health, timestatus_text(res=r)))
        return response
    else:
        return res_health


def timestatus(modified_ago, upd_freq):
    """
    Returns a Bool tuple representing outdated and discontinued flags
    based on parameters modified_ago and upd_freq (update frequency).
    """
    outdated, discontinued = False, False
    try:
        if upd_freq and str(upd_freq).isdigit():
            upd_freq_days = int(upd_freq)
            outdated = 0 < upd_freq_days < modified_ago
            discontinued = (
                upd_freq_days == 1 and modified_ago > 30) or (
                upd_freq_days == 7 and modified_ago > 60) or (
                upd_freq_days == 15 and modified_ago > 90) or (
                upd_freq_days == 30 and modified_ago > 182) or (
                upd_freq_days in (90, 182, 365, 1826) and
                    modified_ago > upd_freq_days + 182)
    except Exception as e:
        print(u'ERROR: %s' % str(e))
    return outdated, discontinued


def timestatus_text(resource_id=None, res=None):
    if resource_id is not None:
        res = Session.query(Resource).get(resource_id)
    update_frequency = res.extras.get('update_frequency', u'')
    res_modified_date = res.last_modified.date() if \
        res.last_modified else res.created.date()
    modified_ago = (date.today() - res_modified_date).days
    outdated, discontinued = timestatus(modified_ago, update_frequency)
    return 'Discontinuado' if discontinued else ('Desactualizado' if outdated else 'Activo')


def get_update_frequency_text(upd_frequency):
    if upd_frequency:
        if upd_frequency == u'-1':
            update_frequency_value = 'Publicacion unica'
        elif upd_frequency == u'0':
            update_frequency_value = 'Enlace externo'
        elif upd_frequency == u'1':
            update_frequency_value = 'Diario'
        elif upd_frequency == u'7':
            update_frequency_value = 'Semanal'
        elif upd_frequency == u'15':
            update_frequency_value = 'Quincenal'
        elif upd_frequency == u'30':
            update_frequency_value = 'Mensual'
        elif upd_frequency == u'60':
            update_frequency_value = 'Bimensual'
        elif upd_frequency == u'90':
            update_frequency_value = 'Trimestral'
        elif upd_frequency == u'182':
            update_frequency_value = 'Semestral'
        elif upd_frequency == u'365':
            update_frequency_value = 'Anual'
        elif upd_frequency == u'1826':
            update_frequency_value = 'Quinquenal'
        else:
            update_frequency_value = 'Desconocido'
    else:
        update_frequency_value = 'Sin especificar'
    return update_frequency_value


def get_resource_url(resource, config, download=True):
    if resource.url.startswith('http'):
        return resource.url
    elif resource.url.startswith('www.'):
        return 'http://' + resource.url
    else:
        url = '%s/dataset/%s/resource/%s/' % (
            config.get('ckan.site_url'), resource.package_id, resource.id)
        return (url + 'download/%s' % resource.url) if download else url
