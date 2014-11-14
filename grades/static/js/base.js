window.addEventListener('load', function() {
    var url = window.location.href;
    console.log(url);
    var navbar = document.getElementById('navbar');
    if(url.indexOf("index") > -1)
        navbar.children[0].className += ' active';
    else if(url.indexOf("about") > -1)
        navbar.children[1].className += ' active';
     else if(url.indexOf("faq") > -1)
        navbar.children[2].className += ' active';
     else if(url.indexOf("report") > -1)
        navbar.children[3].className += ' active';
});

setTimeout(function() {
    $("#message-list").children('.alert:first-child').fadeOut(1000);
}, 5000);
