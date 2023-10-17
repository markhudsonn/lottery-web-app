from flask import Blueprint, render_template

errors_blueprint = Blueprint('errors', __name__, template_folder='templates')


@errors_blueprint.app_errorhandler(400)
def error_400(error):
    return render_template('errors/400.html'), 400


@errors_blueprint.app_errorhandler(403)
def error_403(error):
    return render_template('errors/403.html'), 403


@errors_blueprint.app_errorhandler(404)
def error_404(error):
    return render_template('errors/404.html'), 404


@errors_blueprint.app_errorhandler(500)
def error_500(error):
    return render_template('errors/500.html'), 500


@errors_blueprint.app_errorhandler(503)
def error_503(error):
    return render_template('errors/503.html'), 503
