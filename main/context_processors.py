def config_defaults(request):
    return {'config_defaults': request.session.get('defaults_key', '')}
