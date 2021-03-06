// https://www.w3schools.com/bootstrap/bootstrap_ref_js_scrollspy.asp

// Add smooth scrolling on all links inside the navbar
$(".navbar a").on("click", function (event) {
  // Make sure this.hash has a value before overriding default behavior
  if (this.hash !== "") {
    // Prevent default anchor click behavior
    event.preventDefault()

    // Store hash
    var hash = this.hash

    // Using jQuery's animate() method to add smooth page scroll
    // The optional number (0) specifies the number of milliseconds
    // it takes to scroll to the specified area
    $("html, body").animate(
      {
        scrollTop: $(hash).offset().top - 60,
      },
      0,
      function () {
        // Add hash (#) to URL when done scrolling (default click behavior)
        if (history.pushState) {
          history.pushState(null, null, hash)
        }
      }
    )
  }
})
