const DARK_MODE_KEY = "dark_theme";

function whichTransitionEvent() {
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

function checkForStorage() {
    return typeof(Storage) !== "undefined"
}

function darkModeClass(isDarkMode) {
    isDarkMode ? $('body').addClass("dark") : $('body').removeClass('dark');
}

function darkModeHandler(){
    let darkModeToggle = $('#dark-mode-toggle');

    if (checkForStorage()) {
        let isDarkMode = localStorage.getItem(DARK_MODE_KEY);

        if (isDarkMode === null) {
            darkModeToggle.prop("checked", false);
            darkModeClass(false);
            localStorage.setItem(DARK_MODE_KEY, false);
        } else {
            isDarkMode = JSON.parse(isDarkMode) === true;
            darkModeToggle.prop("checked", isDarkMode);
            darkModeClass(isDarkMode);
        }
    }

    darkModeToggle.on('click', function () {
        let isToggleChecked = darkModeToggle.is(":checked");

        localStorage.setItem(DARK_MODE_KEY, isToggleChecked);
        darkModeClass(isToggleChecked);
    });
}

function passwordHandler() {
    let passwordField = $('#field');
    let passwordViewToggle = $('#password-view-toggle');
    let viewPassword = $('.bi-eye');
    let hidePassword = $('.bi-eye-slash');

    passwordViewToggle.on('click', function () {
        if (passwordViewToggle.is(':checked')) {
            passwordField.attr('type', 'text');
            viewPassword.removeClass('inline-block').addClass('hidden');
            hidePassword.removeClass('hidden').addClass('inline-block');
        } else {
            passwordField.attr('type', 'password');
            viewPassword.addClass('inline-block').removeClass('hidden');
            hidePassword.addClass('hidden').removeClass('inline-block');
        }
    });
}

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

    return element;
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
    let pages = $('.pagination > li').children('.page-link:not(.collapse)');
    let pagesLength = pages.length - 2;

    if (pagesLength <= 6) return;
    
    // Get active page and its index
    let activePage = null,
        activePageIndex = null;

    for (let i = 1; i < pagesLength + 1; i++) {
        if ($(pages[i]).hasClass('active')) {
            activePage = pages[i];

            if (i === 1) {
                activePageIndex = 1;
            } else if (i === pagesLength) {
                activePageIndex = i + 2;
            } else {
                activePageIndex = i + 1;
            }

            break;
        }
    }

    if (activePage === null) return;

    let listItems = $('.pagination').children();
    // first is 2 because previous and 1 page
    // last is -3 because next, last page and index 0
    let firstCollapseIndex = 2,
        lastCollapseIndex = listItems.length - 3;
    
    let firstCollapse = $(listItems[firstCollapseIndex]).children()[0];
    let lastCollapse = $(listItems[lastCollapseIndex]).children()[0];

    // Remove children in first and last collapse
    $('#pagination-collapse-first').children().remove();
    $('#pagination-collapse-last').children().remove();
    
    // Diff -2 because the minimum number in collapse are 2 numbers.
    let firstDiff = activePageIndex - firstCollapseIndex - 2;
    let lastDiff = lastCollapseIndex - activePageIndex - 2;
    
    if (firstDiff > 1 && lastDiff <= 1) {
        // first collapse
        // end index is active - 3 because we want to take the previous pages (2 page numbers, 1 hidden page)
        let endIndex = activePageIndex - 3;
        
        // If end index + 1 (so it can be last page) is last in pages, then - 2, so it can take 3 page numbers before last pages
        if (endIndex+1 == pagesLength) endIndex -= 2;

        // Hide pages after first collapse until end index
        for (let i = firstCollapseIndex + 1; i <= endIndex; i++){
            // Hide the page
            toggleClass($(pages[i-1]), 'hidden');
        }

        // Show the collapse
        toggleClass($(firstCollapse), 'hidden');
    } else if (firstDiff <= 1 && lastDiff > 1) {
        // last collapse
        // start index is active + 3, because we want to take the next pages (1 previous, 1 collapse, 1 page number)
        let startIndex = activePageIndex + 3;
        
        // If active page is first page, then + 2, because it will take 2 page numbers more
        if (activePageIndex === 1) startIndex += 2;
        
        // Hide page at active + 3 until before last collapse
        for (let i = startIndex; i < lastCollapseIndex; i++){
            // Hide the page
            toggleClass($(pages[i-1]), 'hidden');
        }
        
        // Show the collapse
        toggleClass($(lastCollapse), 'hidden');
    } else if(firstDiff > 1 && lastDiff > 1) {
        // both collapse
        // end index is active - 3 because we want to take the previous pages (2 page numbers, 1 hidden page)
        let endIndex = activePageIndex - 3;
        
        // Hide pages after first collapse until end index
        for (let i = firstCollapseIndex + 1; i <= endIndex; i++){
            // Hide the page
            toggleClass($(pages[i-1]), 'hidden');
        }
        // Show the collapse
        toggleClass($(firstCollapse), 'hidden');

        // Last collapse
        // Hide page at active + 3 until before last collapse
        for (let i = activePageIndex + 3; i < lastCollapseIndex; i++) {
            // Hide the page
            toggleClass($(pages[i - 1]), 'hidden');
        }
        // Show the collapse
        toggleClass($(lastCollapse), 'hidden');
    }
}

function checkboxTable(element) {
    let table = $(element);
    
    table
        .find("thead th:nth-child(1) input[type='checkbox']")
            .on("change", function () {
                // When checkbox on table header on change ...
                // If not checked, ...
                console.log($(this).is(":checked"));
                if ($(this).is(":checked")) {
                    // Check all checkboxes that are not disabled and not checked
                    table.find("tbody th:nth-child(1) input[type='checkbox']:not(:disabled):not(:checked)").prop("checked", true).trigger("change");
                } else {
                    // Uncheck all checkboxes that are not disable and checked
                    table.find("tbody th:nth-child(1) input[type='checkbox']:not(:disabled):checked").prop("checked", false).trigger("change");
                }
            }).end()
        .find("tbody tr")
            .on("click", function () {
                // When checkbox on table row in table body on click ...
                // Get checkbox on clicked row
                let checkbox = $(this).find("th:nth-child(1) input[type='checkbox']:not(:disabled)");
                
                // Change checked property
                checkbox.prop("checked", !checkbox.is(":checked")).trigger("change");
            }).end()
        .find("tbody th:nth-child(1) input[type='checkbox']")
            .on("change", function () {
                // When checkbox on table body on change ...
                // Get checked checkboxes
                let checkedCheckboxes = $(this).closest("tbody").find("th:nth-child(1) input[type='checkbox']:not(:disabled):checked");
                let totalCheckboxes = $(this).closest("tbody").find("th:nth-child(1) input[type='checkbox']:not(:disabled)");

                // Change checkbox on table header
                if (checkedCheckboxes.length === 0) {
                    // Uncheck
                    table.find("thead th:nth-child(1) input[type='checkbox']").prop("checked", false);
                    table.find("thead th:nth-child(1) input[type='checkbox']").prop("indeterminate", false);
                } else if (checkedCheckboxes.length === totalCheckboxes.length) {
                    // Check
                    table.find("thead th:nth-child(1) input[type='checkbox']").prop("checked", true);
                    table.find("thead th:nth-child(1) input[type='checkbox']").prop("indeterminate", false);
                } else {
                    // Indeterminate
                    table.find("thead th:nth-child(1) input[type='checkbox']").prop("checked", false);
                    table.find("thead th:nth-child(1) input[type='checkbox']").prop("indeterminate", true);
                }

                // Change tr color
                if ($(this).is(":checked")) {
                    $(this).closest('tr').addClass("active");
                } else {
                    $(this).closest('tr').removeClass("active");
                }
            }).trigger("change").end()
        .find("tbody td a, input[type='checkbox']")
            .on("click", function (e) {
                e.stopPropagation();
            }).end();
}

function tableAccordion(element) {
    toggleClass($(toggleClass($(element).closest('.table-row'), "open")).next(".table-details"), "open");
}

var transitionEvent = whichTransitionEvent();
console.log(transitionEvent);

checkboxTable("table.table-checkbox");
darkModeHandler();
breadcrumb();
pagination();
passwordHandler();
