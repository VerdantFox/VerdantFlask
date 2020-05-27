// Section of javascript to run every time comments are refreshed

// ****************************************************************
// functions
// ****************************************************************

// Blog comments
function expandEdit (commentID) {
    event.preventDefault();
    const commentText = $(`#comment_content_${commentID}`).text().trim();
    $(`textarea#comment_edit_textarea_${commentID}`).val(commentText);
    $(`#comment_content_${commentID}`).hide();
    $(`#comment_edit_${commentID}`).show();
}
function contractEdit (commentID) {
    event.preventDefault();
    $(`#comment_edit_${commentID}`).hide();
    $(`#comment_content_${commentID}`).show();
}
function setCommentEdit (commentID) {
    $('#comment_edit').val(
        $(`textarea#comment_edit_textarea_${commentID}`).val().trim()
    );
}

// Replies
function expandCreateReply (commentID) {
    event.preventDefault();
    $(`textarea#reply_textarea_${commentID}`).val('');
    $(`#reply_button_${commentID}`).hide();
    $(`#create_reply_${commentID}`).show();
}
function contractCreateReply (commentID) {
    event.preventDefault();
    $(`#create_reply_${commentID}`).hide();
    $(`#reply_button_${commentID}`).show();
}
function expandReplyEdit (replyID) {
    event.preventDefault();
    const commentText = $(`#reply_content_${replyID}`).text().trim();
    $(`textarea#reply_edit_textarea_${replyID}`).val(commentText);
    $(`#reply_content_${replyID}`).hide();
    $(`#reply_edit_${replyID}`).show();
}
function contractReplyEdit (replyID) {
    event.preventDefault();
    $(`#reply_edit_${replyID}`).hide();
    $(`#reply_content_${replyID}`).show();
}
function setCreateReply (commentID) {
    $('#reply').val(
        $(`textarea#reply_textarea_${commentID}`).val().trim()
    );
}
function setEditReply (replyID) {
    $('#reply').val(
        $(`textarea#reply_edit_textarea_${replyID}`).val()
    );
}


// ****************************************************************
// actions
// ****************************************************************
$('#cancel-comment').on("click", function(){
    event.preventDefault();
    $("#comment").val('');
});
$("#comment").val('');

