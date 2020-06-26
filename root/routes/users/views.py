import os

from authomatic.adapters import WerkzeugAdapter
from flask import (
    Blueprint,
    Markup,
    abort,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from root.globals import STATIC_PATH
from root.image_handler import delete_current_avatar, upload_avatar
from root.routes.users.forms import (
    LoginForm,
    RegistrationForm,
    UserProfileForm,
    UserSettingsForm,
)
from root.routes.users.models import User
from root.routes.users.oauth_config import authomatic

users = Blueprint("users", __name__)

DEFAULT_AVATARS_PATH = os.path.join(STATIC_PATH, "images", "avatars_default")
DEFAULT_PICS = sorted(os.listdir(DEFAULT_AVATARS_PATH))


@users.route("/register", methods=["GET", "POST"])
def register():
    """Registers the user in 'flask' database, 'users' collection"""
    logout_user()
    session["next"] = request.args.get("next")
    form = RegistrationForm()
    if form.validate_on_submit():
        password_hash = generate_password_hash(form.password.data)
        user = User(
            email=form.email.data,
            username=form.username.data,
            password_hash=password_hash,
            access_level=2,
        )
        user.save()
        flash_register_message(user.username)
        return login_and_redirect(user)
    return render_template("users/register.html", form=form)


@users.route("/login", methods=["GET", "POST"])
def login():
    """Logs the user in through username/password"""
    logout_user()
    session["next"] = request.args.get("next")
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
            return login_and_redirect(user)
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


@users.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    user = User.objects(username=username).first()
    if not user:
        abort(404, "User not found.")
    is_current_user = True if user.id == current_user.id else False
    return render_template(
        "users/profile.html", user=user, is_current_user=is_current_user
    )


@users.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = UserProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.full_name = form.full_name.data if form.full_name.data else None
        current_user.bio = form.bio.data if form.bio.data else None
        if form.birth_date.data:
            current_user.birth_date = form.birth_date.data
        else:
            current_user.birth_date = None
        if form.upload_avatar.data:
            avatar_image = upload_avatar(form.upload_avatar.data)
            if avatar_image is None:
                flash("Invalid image extension type used!", category="error")
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
        current_user.share_name = form.share_name.data
        current_user.share_birth_date = form.share_birth_date.data

        current_user.save()
        flash("User Profile Updated", category="success")
        return redirect(url_for("users.profile", username=current_user.username))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.full_name.data = current_user.full_name
        form.bio.data = current_user.bio
        form.birth_date.data = current_user.birth_date
        form.share_birth_date.data = current_user.share_birth_date
        form.share_name.data = current_user.share_name
    return render_template(
        "users/edit_profile.html", form=form, default_pics=DEFAULT_PICS
    )


@users.route("/account_settings", methods=["GET", "POST"])
@login_required
def account_settings():

    form = UserSettingsForm()
    if form.validate_on_submit():
        if form.email.data:
            current_user.email = form.email.data
        current_user.timezone = form.timezone.data
        if form.password.data:
            new_hash = generate_password_hash(form.password.data)
            current_user.password_hash = new_hash
        current_user.share_email = form.share_email.data
        current_user.share_timezone = form.share_timezone.data
        current_user.save()
        flash("User Account Updated", category="success")
        return redirect(url_for("users.account_settings"))
    elif request.method == "GET":
        form.email.data = current_user.email
        # Only override default if timezone set
        if current_user.timezone:
            form.timezone.data = current_user.timezone
        form.share_email.data = current_user.share_email
        form.share_timezone.data = current_user.share_timezone

    return render_template(
        "users/account_settings.html", form=form, can_disconnect=can_oauth_disconnect()
    )


@users.route("/delete_account")
@login_required
def delete_account():
    """Delete current user's account"""
    current_user.delete()
    logout_user()
    flash("Account deleted!", category="success")
    return redirect(url_for("core.index"))


@users.route("/facebook_oauth")
def facebook_oauth():
    return oauth_generalized("Facebook")


@users.route("/google_oauth")
def google_oauth():
    return oauth_generalized("Google")


@users.route("/github_oauth")
def github_oauth():
    """Perform github oauth register, login, or account association"""
    return oauth_generalized("GitHub")


@users.route("/facebook_oauth_disconnect")
def facebook_oauth_disconnect():
    return oauth_disconnect("Facebook")


@users.route("/google_oauth_disconnect")
def google_oauth_disconnect():
    return oauth_disconnect("Google")


@users.route("/github_oauth_disconnect")
def github_oauth_disconnect():
    return oauth_disconnect("GitHub")


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
    return bool(oauth_count > 1 or (has_email and has_pw))


def oauth_disconnect(oauth_client):
    """Generalized oauth disconnect"""
    if not current_user.is_authenticated:
        return redirect(url_for("users.login"))

    db_oauth_key = str(oauth_client).lower() + "_id"

    current_user[db_oauth_key] = None
    current_user.save()

    flash(f"Disconnected from {oauth_client}!")
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
        flash("Login failed, try again with another method.", category="error")
        return redirect(url_for("users.login"))

    # Update user to retrieve data
    result.user.update()

    db_oauth_key = str(oauth_client).lower() + "_id"

    client_name = result.user.name
    client_oauth_id = result.user.id

    # Check if user in in database with this oauth login already exists
    lookup = {db_oauth_key: client_oauth_id}
    user = User.objects(**lookup).first()

    if current_user.is_authenticated:
        # Oauth method is already linked to an account, do nothing
        if user:
            flash(
                f"That {oauth_client} account is already linked with an account. "
                f"Please log in to that account through {oauth_client} and un-link "
                "it from that account to link it to this account.",
                category="error",
            )
        # Add this oauth method to current user
        else:
            current_user[db_oauth_key] = client_oauth_id
            current_user.save()
        # Should only get here from "settings" so return there
        return redirect(url_for("users.account_settings"))

    # Register a new user with this oauth authentication method
    if not user:
        # Generate a unique username from client's name found in oauth lookup
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
        # Create user and save to database
        user_data = {
            "username": username,
            "full_name": client_name,
            db_oauth_key: client_oauth_id,
            "access_level": 2,
        }
        user = User(**user_data)
        user.save()
        flash_register_message(user.username)

    # Else user was found and is now authenticated
    # Log in the found or created user
    return login_and_redirect(user)


def login_and_redirect(user):
    """Logs in user and redirects to 'next' in session, or index otherwise"""
    login_user(user)
    flash(f"Welcome {user.username}!", category="success")
    next_page = session.pop("next", None)
    if isinstance(next_page, str):
        for path in ("login", "register"):
            if path in next_page:
                return redirect(url_for("core.index"))
    else:
        next_page = url_for("core.index")
    return redirect(next_page)


def flash_register_message(username):
    """Flash a welcome message for newly registered user"""
    flash(f"Thanks for registering, {username}!", category="success")
    flash(
        Markup(
            "You can change your username and profile picture in the "
            f"<a href='{url_for('users.edit_profile')}' "
            "class='c-blue'>edit profile</a> page."
        )
    )
