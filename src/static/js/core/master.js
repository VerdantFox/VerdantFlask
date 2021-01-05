// Blog Stuff
$(".blog-view table").addClass("table")
$(".blog-view table").addClass("table-dark")
$(".blog-view table").addClass("table-striped")
$(".blog-view table").addClass("table-hover")
$("#search-submit").on("click", function () {
  var search = $("#blog-search").val()
  window.location = "/blog?search=" + search
})
$("#blog-search").keydown(function (event) {
  // Number 13 is the "Enter" key on the keyboard
  if (event.keyCode === 13) {
    event.preventDefault()
    document.getElementById("search-submit").click()
  }
})

// dropdown submenu capabilities
function readyDropdownSubmenus() {
  $(".dropdown-submenu button.subdrop").on("click", function (e) {
    $(this).next("div").toggle()
    e.stopPropagation()
    e.preventDefault()
  })
}
$(document).ready(readyDropdownSubmenus)
