$(".default-avatar").on("click", function (event) {
  event.stopPropagation()
  event.stopImmediatePropagation()
  $(".default-avatar").removeClass("avatar-selected")
  $(this).addClass("avatar-selected")
  $("#select_avatar").val($(this).attr("id"))
})
