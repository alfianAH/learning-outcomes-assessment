function whichTransitionEvent(){
    var t, el = document.createElement("fakeelement");

    var transitions = {
        "transition"      : "transitionend",
        "OTransition"     : "oTransitionEnd",
        "MozTransition"   : "transitionend",
        "WebkitTransition": "webkitTransitionEnd"
    }

    for (t in transitions){
        if (el.style[t] !== undefined){
            return transitions[t];
        }
    }
}
  
var transitionEvent = whichTransitionEvent();
console.log(transitionEvent);

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
    const backdrop = $('.sidebar-backdrop');
    backdrop.removeClass('hidden').addClass('fade show');

    // Show sidebar
    target.one(transitionEvent, function () {
        target.removeClass('showing').addClass('show');
    });
    
    backdrop.on('click', function () {
        closeSidebar(target, backdrop);
    });
}

function closeSidebar(sidebar, backdrop) {
    // Hide sidebar
    sidebar.addClass('hiding');

    sidebar.one(transitionEvent, function () {
        // Remove backdrop
        backdrop.removeClass('fade show').addClass('hidden');
        // Remove sidebar's classses
        sidebar.removeClass('hiding show');
    });
}

function resetSidebarToDefault() {
    if ($(window).width() >= 1024) {
        // Remove backdrop
        $('.sidebar-backdrop').removeClass('fade show').addClass('hidden');

        // Remove sidebar's classses
        $('.sidebar').removeClass('hiding show');
    }
}

window.onresize = function () {
    resetSidebarToDefault();
}

function toggleClass(element, className) {
    let currentClass = element.attr('class');

    if (currentClass !== undefined && currentClass.includes(className)) {
        element.removeClass(className);
    } else {
        element.addClass(className);
    }
}

$('.dropdown > summary').on('click', function () {
    toggleClass($('body'), 'noscroll');
});

function breadcrumb() {
    let breadcrumbs = $('.breadcrumb').children('.breadcrumb-item');

    if (breadcrumbs.length <= 4) return;

    let collapseBreadcrumbs = {}
    
    for (let i = 1; i < breadcrumbs.length - 2; i++){
        let breadcrumbText = breadcrumbs[i].innerText;
        let breadcrumbLink = breadcrumbs[i].children[0];
        collapseBreadcrumbs[breadcrumbLink] = breadcrumbText;
        $(breadcrumbs[i]).addClass('hidden');
    }

    toggleClass($('.breadcrumb-item-collapse'), 'hidden');

    for (let key in collapseBreadcrumbs){
        $('#breadcrumb-collapse').append(`<a class='dropdown-item' href='${key}'>${collapseBreadcrumbs[key]}</a>`);
    }
}

breadcrumb();