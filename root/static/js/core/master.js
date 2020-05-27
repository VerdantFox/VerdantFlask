// DEFINE FUNCTIONS

// http://jquery.eisbehr.de/lazy/example_basic-usage
$(function() {
    $('.lazy').lazy();
});


// RUN CODE

// Blog Stuff
$('.blog-view table').addClass('table');
$('.blog-view table').addClass('table-dark');
$('.blog-view table').addClass('table-striped');
$('.blog-view table').addClass('table-hover');
$('#search-submit').on("click", function(){
    var search = $("#blog-search").val();
    window.location = "/blog?search=" + search;
});
$('#blog-search').keydown(function(event) {
    // Number 13 is the "Enter" key on the keyboard
    if (event.keyCode === 13) {
        event.preventDefault();
        document.getElementById('search-submit').click();
    };
});
