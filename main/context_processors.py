import json

def config_defaults(request):
    pretty_json = None
    try:
        pretty_json = json.dumps(
            json.loads(request.session.get('response_text', '')),
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )
    except Exception as e:
        # swallow JSON parsing errors
        pass
    return {
        'config_defaults': request.session.get('defaults_key', ''),
        'curl_command': request.session.get('curl_command', ''),
        'response_status': request.session.get('response_status', ''),
        'response_text': request.session.get('response_text', ''),
        'response_json': pretty_json
    }
