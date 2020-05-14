import os

from authomatic.adapters import WerkzeugAdapter
from flask import (
    Blueprint,
    Markup,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from root.externals import STATIC_PATH
from root.users.forms import (
    LoginForm,
    RegistrationForm,
    UserProfileForm,
    UserSettingsForm,
)
from root.users.image_handler import delete_current_avatar, upload_avatar
from root.users.models import User
from root.users.oauth_config import authomatic

users = Blueprint("users", __name__)

OAUTH_LOOKUP = {
    "github": {"oname": "GitHub", "db_oid": "github_id", "db_oname": "github_name"},
    "facebook": {
        "oname": "Facebook",
        "db_oid": "facebook_id",
        "db_oname": "facebook_name",
    },
    "google": {"oname": "Google", "db_oid": "google_id", "db_oname": "google_name"},
}
DEFAULT_AVATARS_PATH = os.path.join(STATIC_PATH, "images", "avatars_default")
DEFAULT_PICS = sorted(os.listdir(DEFAULT_AVATARS_PATH))


@users.route("/register", methods=["GET", "POST"])
def register():
    """Registers the user in 'flask' database, 'users' collection"""
    logout_user()
    form = RegistrationForm()
    if form.validate_on_submit():
        password_hash = generate_password_hash(form.password.data)
        user = User(
            email=form.email.data,
            username=form.username.data,
            password_hash=password_hash,
        )
        user.save()
        flash("Thanks for registering! Now you can login!", category="success")
        return redirect(url_for("users.login"))
    return render_template("users/register.html", form=form)


@users.route("/login", methods=["GET", "POST"])
def login():
    """Logs the user in"""
    logout_user()
    form = LoginForm()
    if form.validate_on_submit():
        # Grab the user from our User Models table
        username_or_email = form.username_or_email.data
        if "@" in username_or_email:
            user = User.objects(email=username_or_email).first()
        else:
            user = User.objects(username=username_or_email).first()
        # User validates
        if user is not None and user.check_password(form.password.data):
            login_and_redirect(user)
        else:
            flash(
                "(email or username)/password combination not found", category="error"
            )

    return render_template("users/login.html", form=form)


@users.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have logged out.", category="success")
    return redirect(url_for("users.login"))


@users.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    return render_template("users/profile.html")


@users.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = UserProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        if form.full_name.data:
            current_user.full_name = form.full_name.data
        else:
            current_user.full_name = None
        if form.bio.data:
            current_user.bio = form.bio.data
        else:
            current_user.bio = None
        if form.birth_date.data:
            current_user.birth_date = form.birth_date.data
        else:
            current_user.birth_date = None
        if form.upload_avatar.data:
            avatar_image = upload_avatar(form.upload_avatar.data)
            if avatar_image is None:
                return redirect(url_for("users.edit_profile"))
            current_user.avatar_location = url_for(
                "static", filename=f"images/avatars_uploaded/{avatar_image}"
            )
        elif form.select_avatar.data:
            avatar_image = secure_filename(form.select_avatar.data)
            delete_current_avatar()
            current_user.avatar_location = url_for(
                "static", filename=f"images/avatars_default/{avatar_image}"
            )
        current_user.save()
        flash("User Profile Updated", category="success")
        return redirect(url_for("users.profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.full_name.data = current_user.full_name
        form.bio.data = current_user.bio
        form.birth_date.data = current_user.birth_date
    return render_template(
        "users/edit_profile.html", form=form, default_pics=DEFAULT_PICS
    )


@users.route("/account_settings", methods=["GET", "POST"])
@login_required
def account_settings():

    form = UserSettingsForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.timezone = form.timezone.data
        current_user.email = form.email.data
        if form.new_pass.data:
            new_hash = generate_password_hash(form.new_pass.data)
            current_user.password_hash = new_hash
        current_user.save()
        flash("User Account Updated", category="success")
        return redirect(url_for("users.account_settings"))
    elif request.method == "GET":
        form.email.data = current_user.email
        # Only override default if timezone set
        if current_user.timezone:
            form.timezone.data = current_user.timezone

    return render_template(
        "users/account_settings.html", form=form, can_disconnect=can_oauth_disconnect()
    )


@users.route("/delete_account", methods=["GET", "POST"])
def delete_account():
    """Delete current user's account"""
    current_user.delete()
    current_user.save()
    logout_user()
    flash("Account deleted!", category="success")
    return redirect("/")


@users.route("/facebook_oauth", methods=["GET", "POST"])
def facebook_oauth():
    return oauth_generalized("facebook")


@users.route("/google_oauth", methods=["GET", "POST"])
def google_oauth():
    return oauth_generalized("google")


@users.route("/github_oauth", methods=["GET", "POST"])
def github_oauth():
    """Perform github oauth register, login, or account association"""
    return oauth_generalized("github")


@users.route("/facebook_oauth_disconnect", methods=["GET", "POST"])
def facebook_oauth_disconnect():
    return oauth_disconnect("facebook")


@users.route("/google_oauth_disconnect", methods=["GET", "POST"])
def google_oauth_disconnect():
    return oauth_disconnect("google")


@users.route("/github_oauth_disconnect", methods=["GET", "POST"])
def github_oauth_disconnect():
    return oauth_disconnect("github")


# ----------------------------------------------------------------------------
# HELPER METHODS
# ----------------------------------------------------------------------------
def can_oauth_disconnect():
    """Test to determin if oauth disconnect is allowed"""
    has_gh = True if current_user.github_id else False
    has_gg = True if current_user.google_id else False
    has_fb = True if current_user.facebook_id else False
    has_email = True if current_user.email else False
    has_pw = True if current_user.password_hash else False

    oauth_count = [has_gh, has_gg, has_fb].count(True)
    if oauth_count > 1 or (has_email and has_pw):
        return True
    else:
        return False


def oauth_disconnect(oauth_client):
    """Generalized oauth disconnect"""
    if not current_user.is_authenticated:
        return redirect(url_for("users.login"))

    oname = OAUTH_LOOKUP[oauth_client]["oname"]
    db_oid = OAUTH_LOOKUP[oauth_client]["db_oid"]
    db_oname = OAUTH_LOOKUP[oauth_client]["db_oname"]

    current_user[db_oid] = None
    current_user[db_oname] = None
    current_user.save()
    print(current_user)

    flash(f"Disconnected from {oname}!")
    return redirect(url_for("users.account_settings"))


def oauth_generalized(oauth_client):
    """Generalized oauth login, register, and account association"""
    # Get response object for the WerkzeugAdapter.
    response = make_response()
    # Log the user in, pass it the adapter and the provider name.
    result = authomatic.login(WerkzeugAdapter(request, response), oauth_client)

    # If there is no LoginResult object, the login procedure is still pending.
    if not result:
        return response

    if not result.user:
        print("AUTH FAILED")
        return redirect(url_for("users.login"))

    # Update user to retrieve data
    result.user.update()

    oname = OAUTH_LOOKUP[oauth_client]["oname"]
    db_oid = OAUTH_LOOKUP[oauth_client]["db_oid"]
    db_oname = OAUTH_LOOKUP[oauth_client]["db_oname"]

    client_oid = result.user.id
    client_name = result.user.name

    lookup = {db_oid: client_oid}
    user = User.objects(**lookup).first()
    if current_user.is_authenticated:
        if user:
            flash(
                f"That {oname} account is already linked with an account. "
                f"Please log in to that account through {oname} and un-link "
                "it from that account to link it to this account.",
                category="error",
            )
        else:
            current_user[db_oid] = client_oid
            current_user[db_oname] = client_name
            current_user.save()
        return redirect(url_for("users.account_settings"))

    if user:
        flash(f"Welcome {user.username}!")
    else:
        base_username = client_name.lower().split()[0]
        username = base_username
        attempts = 0
        while True:
            user = User.objects(username=username).first()
            if user:
                attempts += 1
                username = base_username + str(attempts)
            else:
                break
        user_data = {
            "username": username,
            "full_name": client_name,
            db_oid: client_oid,
            db_oname: client_name,
        }
        user = User(**user_data)
        user.save()
        flash(f"Registered user {user.username}!")
        flash(
            Markup(
                "You can change your username in "
                f"<a href='{url_for('users.account_settings')}' "
                "class='c-4'>account settings</a>."
            )
        )

    return login_and_redirect(user)


def login_and_redirect(user):
    login_user(user)
    return redirect_next()


def redirect_next():
    next = request.args.get("next")
    if next is None or not next[0] == "/":
        next = url_for("core.index")
    return redirect(next)
