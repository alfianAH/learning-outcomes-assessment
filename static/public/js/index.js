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

function pagination() {
    let pages = $('.pagination > li').children('.page-link');
    let pagesLength = pages.length - 2;

    if (pagesLength <= 5) return;
    
    // Get active, previous, and next page
    let activePage = null,
        previousPage = null,
        nextPage = null,
        activePageIndex = null;

    for (let i = 1; i < pagesLength + 1; i++) {
        if ($(pages[i]).hasClass('active')) {
            activePage = pages[i];

            if (i !== 1) {
                previousPage = pages[i - 1];
                activePageIndex = i + 1;
            }
            if (i !== pagesLength) {
                nextPage = pages[i + 1];
                activePageIndex = i + 1;
            }
            if (i === 1) activePageIndex = 1;
            // 2 because skip 2 collapses
            if (i === pagesLength) activePageIndex = i + 2;

            break;
        }
    }

    if (activePage === null) return;

    let listItems = $('.pagination').children();
    // first is 2 because previous and 1 page
    // last is -3 because next, last page and index 0
    let firstCollapseIndex = 2,
        lastCollapseIndex = listItems.length - 3;
    
    let firstCollapse = $($($($($(listItems[firstCollapseIndex]).children()[0]).children()[0]).children()[0]).children()[0]);
    let lastCollapse = $($($($($(listItems[lastCollapseIndex]).children()[0]).children()[0]).children()[0]).children()[0]);

    // Remove children in first and last collapse
    $('#pagination-collapse-first').children().remove();
    $('#pagination-collapse-last').children().remove();
    
    let firstDiff = activePageIndex - firstCollapseIndex;
    let lastDiff = lastCollapseIndex - activePageIndex;
    
    if (firstDiff > lastDiff) {
        // first collapse
        console.log('first');
        // end index is active - 2 because we want to take the previous page (1 page number)
        let endIndex = activePageIndex - 2;
        
        // If end index is last in pages, then - 1, so it can take 2 page numbers before last pages
        if (endIndex == pagesLength) endIndex -= 2;

        for (let i = firstCollapseIndex + 1; i <= endIndex; i++){
            // Append page to collapse
            $('#pagination-collapse-first').append(`<a class='dropdown-item' href='#'>${pages[i - 1].innerText}</a>`)
            // Hide the page
            toggleClass($(pages[i-1]), 'hidden');
        }

        // Show the collapse
        toggleClass($(firstCollapse), 'hidden');
    } else if (firstDiff < lastDiff) {
        // last collapse
        console.log('last');
        // start index is active + 2, because we want to take the next page (1 page number)
        let startIndex = activePageIndex + 2;
        
        // If active page is first page, then + 2, because it will take first collapse and 1 page number more
        if (activePageIndex === 1) startIndex += 2;
        
        for (let i = startIndex; i < lastCollapseIndex; i++){
            // Append page to collapse
            $('#pagination-collapse-last').append(`<a class='dropdown-item' href='#'>${pages[i - 1].innerText}</a>`)
            // Hide the page
            toggleClass($(pages[i-1]), 'hidden');
        }
        
        // Show the collapse
        toggleClass($(lastCollapse), 'hidden');
    } else {
        // both collapse
        console.log('both');
        // end index is active - 2 because we want to take the previous page (1 page number)
        let endIndex = activePageIndex - 2;
        
        for (let i = firstCollapseIndex + 1; i <= endIndex; i++){
            // Append page to collapse
            $('#pagination-collapse-first').append(`<a class='dropdown-item' href='#'>${pages[i - 1].innerText}</a>`)
            // Hide the page
            toggleClass($(pages[i-1]), 'hidden');
        }
        // Show the collapse
        toggleClass($(firstCollapse), 'hidden');

        // Last collapse
        for (let i = activePageIndex + 2; i < lastCollapseIndex; i++) {
            // Append page to collapse
            $('#pagination-collapse-last').append(`<a class='dropdown-item' href='#'>${pages[i - 1].innerText}</a>`)
            // Hide the page
            toggleClass($(pages[i - 1]), 'hidden');
        }
        // Show the collapse
        toggleClass($(lastCollapse), 'hidden');
    }
}

breadcrumb();
pagination();