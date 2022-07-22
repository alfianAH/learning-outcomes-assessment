const darkModeToggle = $('#dark-mode-toggle');
const html = $('html');

darkModeToggle.on('click', function(){
    darkModeToggle.is(':checked') ? html.addClass('dark') : html.removeClass('dark');
});

const passwordField = $('#field');
const passwordViewToggle = $('#password-view-toggle');
const viewPassword = $('.bi-eye');
const hidePassword = $('.bi-eye-slash');

passwordViewToggle.on('click', function(){
    if(passwordViewToggle.is(':checked')){
        passwordField.attr('type', 'text');
        viewPassword.removeClass('inline-block').addClass('hidden');
        hidePassword.removeClass('hidden').addClass('inline-block');
    } else{
        passwordField.attr('type', 'password');
        viewPassword.addClass('inline-block').removeClass('hidden');
        hidePassword.addClass('hidden').removeClass('inline-block');
    }
})

function showSidebar(button){
    const targetId = $(button).attr('data-target');

    const target = $(targetId);
    // Showing sidebar
    target.addClass('showing');
    // Show backdrop
    target.after($('<div>').addClass('offcanvas-backdrop fade show'));

    // Show sidebar
    target.one("webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend", function () {
        target.removeClass('showing').addClass('show');
    });

    const backdrop = $('.offcanvas-backdrop');
    
    backdrop.on('click', function () {
        // Hide sidebar
        target.addClass('hiding');

        target.one("webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend", function () {
            // Remove backdrop
            backdrop.remove();
            // Remove sidebar's classses
            target.removeClass('hiding show');
        });
    });
}