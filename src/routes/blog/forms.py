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

from src.custom_form_validators import unique_blog_title


class CommentForm(FlaskForm):
    """Form for commenting on blog posts or replying to comments"""

    comment = HiddenField("Comment", validators=[Length(max=500)])
    submit = SubmitField("Submit")


class EditBlogPostForm(FlaskForm):
    """Form for creating/editing a blog post"""

    next_page = HiddenField("Next Page", description="Next Page")
    title = StringField(
        "Title",
        description="Title",
        validators=[DataRequired(), Length(max=200)],
    )
    tags = StringField(
        "Tags",
        description="Comma separated list of tags",
        validators=[Optional(), Length(max=200)],
    )
    publish = BooleanField("Publish", description="publish", default=False)
    can_comment = BooleanField("Can Comment", description="Can Comment", default=True)
    description = TextAreaField(
        "Description",
        description="Short Markdown Description (couple paragraphs)",
        validators=[DataRequired(), Length(max=50_000)],
    )
    content = TextAreaField(
        "Content",
        description="Markdown Content (The Whole Blog Post)",
        validators=[DataRequired(), Length(max=500_000)],
    )
    submit = SubmitField("Submit")


class CreateBlogPostForm(EditBlogPostForm):
    """Create blog post form"""

    title = StringField(
        "Title",
        description="Title",
        validators=[DataRequired(), Length(max=200), unique_blog_title()],
    )


class EditImagesForm(FlaskForm):
    upload_image = FileField(
        "Upload an Image",
        description="Upload an Image",
    )
    image_name = StringField("Image Name", description="Image name")
    delete_image = HiddenField("Delete Image", description="Delete Image")
    submit_image = SubmitField("Upload Image")
