from flask import Blueprint, render_template

error_pages = Blueprint("error_pages", __name__)


@error_pages.app_errorhandler(404)
def error_404(error):
    """Error for pages not found."""
    default = (
        "The requested URL was not found on the server. "
        "If you entered the URL manually please check your spelling and try again."
    )
    if error.description == default:
        error.description = "Oops! The page you requested was not found."
    return render_template("error_pages/all_errors.html", error=error), 404


@error_pages.app_errorhandler(500)
def error_500(error):
    """Error for pages not found."""
    default = (
        "The server encountered an internal error and was unable to complete your "
        "request. Either the server is overloaded or there is an error in the application."
    )
    if error.description == default:
        error.description = "Something went wrong. It's not you, it's us..."
    return render_template("error_pages/all_errors.html", error=error), 500


@error_pages.app_errorhandler(401)
def error_401(error):
    """Error for trying to access something without authorization."""
    return render_template("error_pages/all_errors.html", error=error), 401


@error_pages.app_errorhandler(403)
def error_403(error):
    """Error for trying to access something which is forbidden."""
    return render_template("error_pages/all_errors.html", error=error), 403
