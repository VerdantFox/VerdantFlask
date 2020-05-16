# Form Based Imports
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    FileField,
    HiddenField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, Optional


class CommentForm(FlaskForm):
    """Form for commenting on blog posts or replying to comments"""

    comment = TextAreaField(
        "Comment", description="Comment", validators=[DataRequired(), Length(max=200)],
    )
    submit = SubmitField("Submit")


class EditBlogPostForm(FlaskForm):
    """Form for editing a blog post"""

    publish = BooleanField("Publish", description="publish", default=False)
    title = StringField(
        "Title", description="Title", validators=[DataRequired(), Length(max=200)],
    )
    content = TextAreaField(
        "Content",
        description="Content",
        validators=[DataRequired(), Length(max=10_000)],
    )
    images = FileField("Images", description="Upload avatar", validators=[Optional()])
    tags = StringField(
        "Tags",
        description="Comma separated list of tags",
        validators=[Optional(), Length(max=200)],
    )
    submit = SubmitField("Submit")


class SearchForm(FlaskForm):
    """Form for searching against blog posts"""

    page = HiddenField("Page", default=1)
    search = StringField("Search", description="search", validators=[Optional()])
    submit = SubmitField("Search")
