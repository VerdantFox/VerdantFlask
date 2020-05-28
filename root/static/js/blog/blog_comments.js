// Section of javascript to run every time comments are refreshed

// ****************************************************************
// functions
// ****************************************************************

// Blog comments
function mainCommentCancel (textarea_id) {
    event.preventDefault();
    $("#comment_textarea_main").val('');
    hideError(textarea_id);
}
function setComment (id) {
    event.preventDefault();
    $('#comment').val(
        $(`textarea#${id}`).val().trim()
    );
    checkCommentLength(id);
}
function expandEdit (commentID) {
    event.preventDefault();
    const commentText = $(`#comment_content_${commentID}`).text().trim();
    $(`textarea#comment_edit_textarea_${commentID}`).val(commentText);
    $(`#comment_content_${commentID}`).hide();
    $(`#comment_edit_${commentID}`).show();
}
function contractEdit (commentID, textarea_id) {
    event.preventDefault();
    $(`#comment_edit_${commentID}`).hide();
    $(`#comment_content_${commentID}`).show();
    hideError(textarea_id);
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
function contractCreateReply (commentID, textarea_id) {
    event.preventDefault();
    $(`#create_reply_${commentID}`).hide();
    $(`#reply_button_${commentID}`).show();
    hideError(textarea_id);
}
function expandReplyEdit (replyID) {
    event.preventDefault();
    const commentText = $(`#reply_content_${replyID}`).text().trim();
    $(`textarea#reply_edit_textarea_${replyID}`).val(commentText);
    $(`#reply_content_${replyID}`).hide();
    $(`#reply_edit_${replyID}`).show();
}
function contractReplyEdit (replyID, textarea_id) {
    event.preventDefault();
    $(`#reply_edit_${replyID}`).hide();
    $(`#reply_content_${replyID}`).show();
    hideError(textarea_id);
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

// multi-scope
function checkCommentLength (textarea_id) {
    $(document).on('beforeAjaxSend.ic', function(event, ajaxSetup, elt){
        if ($(`#${textarea_id}`).val().length > 500) {
            ajaxSetup.cancel = true;
            const error_p_id = `${textarea_id}_error_p`;
            $(`#${error_p_id}`).show();
        } else {
            ajaxSetup.cancel = false;
        }
    });
};
function hideError (textarea_id) {
    const error_p_id = `${textarea_id}_error_p`;
    $(`#${error_p_id}`).hide();
};


// ****************************************************************
// actions
// ****************************************************************

