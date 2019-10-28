document.addEventListener("DOMContentLoaded", function(){
    
    var header = document.querySelector('header'),
    scrolling = false,
    previousTop = 0,
    scrollDelta = 10,
    scrollOffset = 150;

    window.addEventListener('scroll', function() {
        if( !scrolling ) {
            scrolling = true;
            (!window.requestAnimationFrame) ? setTimeout(autoHideHeader, 250) : requestAnimationFrame(autoHideHeader);
        }
    });

    function autoHideHeader() {
        var currentTop = window.scrollY;
        var isNavOpen = document.body.classList.contains('nav-open');
        if (!isNavOpen) {
            if (previousTop - currentTop > scrollDelta) {
                // if scrolling up...
                header.classList.remove('up');
            } else if( currentTop - previousTop > scrollDelta && currentTop > scrollOffset) {
                // if scrolling down...
                header.classList.add('up');
            }
        }
        previousTop = currentTop;
        scrolling = false;
    }
    
    // toggle menu
    var toggleMenuButtons = document.querySelectorAll('.toggle-menu');
    var menu = document.querySelector('.menu');

    Array.prototype.forEach.call(toggleMenuButtons, function( btn ) {
        btn.addEventListener('click', function(event) {
            menu.classList.toggle('active');
        })
    });
    
    // set custom file input events
    var filefields = document.querySelectorAll('.file-field');

    Array.prototype.forEach.call(filefields, function( filefield ) {
        var info = filefield.querySelector('.info'),
            infoVal = info.innerHTML,
            input = filefield.querySelector('input');

        input.addEventListener('change', function( e ) {
            var fileName = '';

            if ( this.files && this.files.length > 1 ) {
                fileName = this.files.length + " file(s) selected";
            } else {
                fileName = e.target.value.split( '\\' ).pop();
            }

            if ( fileName ) {
                info.innerHTML = fileName;
            } else {
                info.innerHTML = infoVal;
            }
        });
    });

    // initialize flatpickrs
    var flatpickrs = document.querySelectorAll('[data-flatpickr]');

    Array.prototype.forEach.call(flatpickrs, function( pkr ) {
        var opts = JSON.parse(pkr.dataset.flatpickr);
        flatpickr(pkr, opts);
    });
    
});