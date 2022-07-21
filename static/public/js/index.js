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
    target.addClass('show');
    
    $('body').append($('<div>').addClass('offcanvas-backdrop fade'));

    const backdrop = $('.offcanvas-backdrop');

    backdrop.addClass('show');

    backdrop.on('click', function(){
        backdrop.removeClass('show');
        target.removeClass('show');
    });
}