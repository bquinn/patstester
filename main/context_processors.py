def config_defaults(request):
    return {'config_defaults': request.session['defaults_key']}
