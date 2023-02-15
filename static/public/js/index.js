const DARK_MODE_KEY = "dark_theme";
var grid = $('.masonry').masonry({
    // options
    itemSelector: 'li',
});

var debounce = function (fn, delay) {
    let timer;
    return function () {
        clearTimeout(timer);
        timer = setTimeout(fn, delay);
    };
};

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
    let passwordField = $('#id_password');
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
    toggleClass($('body'), 'noscroll');
    // Show backdrop
    const backdrop = $('.backdrop');
    backdrop.removeClass('hidden').addClass('fade show');

    // Show sidebar
    target.one(transitionEvent, function () {
        target.removeClass('showing').addClass('show');
    });
    
    backdrop.one('click', function () {
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
    toggleClass($('body'), 'noscroll');
}

function resetSidebarToDefault() {
    if ($('.sidebar').hasClass('show')) {
        if ($(window).width() >= 1024) {
            // Remove backdrop
            $('.backdrop').removeClass('fade show').addClass('hidden');

            // Remove sidebar's classses
            $('.sidebar').removeClass('hiding show');
            toggleClass($('body'), 'noscroll');
        }
    }
}

function openModal(modal) {
    // Showing modal
    $(modal).addClass('showing');
    toggleClass($('body'), 'noscroll');
    // Show backdrop
    const backdrop = $('.backdrop');
    backdrop.removeClass('hidden').addClass('fade show');

    // Show modal
    $(modal).one(transitionEvent, function () {
        $(modal).removeClass('showing').addClass('show');

        // Hide tooltip on modal body scroll
        setTimeout(function () {
            let modalBody = $(modal).find('.modal-body');
            console.log(modalBody);
            $(modalBody).on("scroll", function () {
                $('.tooltip').hide();
            })
        }, 500);
    });
}

function openModalByButton(button) {
    const targetId = $(button).attr('data-target');

    const modal = $(targetId);
    openModal(modal);
}

function closeModal(modal, backdrop) {
    // Hide modal
    modal.addClass('hiding');

    modal.one(transitionEvent, function () {
        // Remove backdrop
        backdrop.removeClass('fade show').addClass('hidden');
        // Remove modal's classses
        modal.removeClass('hiding show');
    });
    toggleClass($('body'), 'noscroll');
}

function closeModalByButton(button) {
    const targetClass = $(button).attr('data-dismiss');
    const modal = $(`.${targetClass}`);
    const backdrop = $('.backdrop');

    closeModal(modal, backdrop);
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
    let currentDropdown = $(this).parent('.dropdown');
    // If close dropdown, ...
    if ($(currentDropdown).prop('open')) {
        $('body').removeClass('noscroll');
    } else { // If open dropdown, ...
        for (let dropdown of $('.dropdown')) {
            if ($(dropdown).is($(currentDropdown))) continue;
            if ($(dropdown).prop('open')) {
                $(dropdown).prop('open', false);
            }
        }
        $('body').addClass('noscroll');
    }
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
    let pages = $('.pagination > li').children('.page-link:not(.page-link-collapse)');
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
    let tableID = $(element).attr('id');
    let table = $(`table#${tableID}`);
    
    table
        .find("thead th:nth-child(1) input[type='checkbox']")
            .on("change", function () {
                // When checkbox on table header on change ...
                // If not checked, ...
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
        .find("tbody td a, input[type='checkbox'], .table-collapse, .table-actions")
            .on("click", function (e) {
                e.stopPropagation();
            }).end();
}

function listItemCheckbox(element) {
    /**
     * Add active class to list item view when checkbox on change
     * to make transition
     */
    let listItemClass = $(element);

    listItemClass.find("input[type='checkbox']").on("change", function () {
        let listItem = $(this).closest(element);
        $(this).is(":checked") ? listItem.addClass("active") : listItem.removeClass("active")
    }).trigger("change");
}

function tableAccordion(element) {
    toggleClass($(toggleClass($(element).closest('tr'), "open")).next(".table-details"), "open");
}

function tabElement() {
    $(".tab-item").on("click", function () {
        let activeTab = $('.tab').find(".tab-item:not(.disabled)");

        if ($(activeTab).is($(this))) return;

        let clickedTab = $(this);
        let activeTabContent = $('.tab-content').find(".show.active");
        let clickedTabContent = $(clickedTab.attr('data-target'));

        // Tabs classes
        activeTab.addClass("disabled");
        clickedTab.removeClass("disabled");

        // Tab contents classes
        activeTabContent.removeClass("show");
        clickedTabContent.addClass("active");
        $('.masonry').masonry('layout');

        activeTabContent.one(transitionEvent, function () {
            activeTabContent.removeClass("active");
            clickedTabContent.addClass("show");
        });
    });
}

function listItemCollapse(element) {
    let targetClass = $(element).attr('data-target');
    toggleClass($(element).closest(targetClass), "open");
    grid.masonry('layout');
}

function listItemRowCollapse(element) {
    let listItem = $(element);

    listItem.on("click", function () {
        toggleClass($(this), "open");
        grid.masonry('layout');
    });
}

function searchText(textElement, dataElement, searchedValue) {
    let data = $(textElement).text();
    let searchResult = data.toLowerCase().indexOf(searchedValue);

    $(dataElement).css('display', searchResult > -1 ? '' : 'none');
}

function searchTextInList(formId) {
    let searchedValue = $('#search-input').val().toLowerCase();
    
    let list = $(`ol#${formId}`);
    let listItems = $(list).find('li');
    
    let tbody = $(`table#${formId}`).find('tbody');
    let trows = $(tbody).find('tr');

    rowsLength = listItems.length;
    if (rowsLength == 0) {
        rowsLength == trows.length;
    }
  
    for (let i = 0; i < rowsLength; i++) {
        let listItem = $(listItems[i]).find('.list-item-title');
        let column = $(trows[i]).find('td.field-nama');
        
        searchText(listItem, listItems[i], searchedValue);
        searchText(column, trows[i], searchedValue);
    }
}

function addToast(toastType = 'info', message) {
    let toastContainer = $('.toast-container');
    let toastElement = toastContainer.find(`.toast-example.${toastType}`).clone(true);

    toastElement.find('.toast-body').text(message);
    toastContainer.append(toastElement);

    // Remove hide from toast
    toastElement.removeClass('toast-example hidden');

    // Set timeout to make fade transition. I don't know why.
    setTimeout(function () {
        toastElement.addClass('show');
        
        toastElement.one(transitionEvent, function () {
            // Remove show after 3s
            setTimeout(function () {
                removeToast(toastElement);
            }, 3000);
        });
    }, 150);
}

function removeToast(toastElement) {
    $(toastElement).removeClass('show');
                
    $(toastElement).one(transitionEvent, function () {
        $(toastElement).remove();
    });
}

function closeToast(buttonElement) {
    let toast = $(buttonElement).closest('.toast');
    removeToast(toast);
}

function toastHandler() {
    const TOAST_LIMIT = 3;

    $('.toast-container').on('DOMNodeInserted', function (event) {
        let children = $(this).children('.toast:not(.toast-example)');
        if (children.length == 0) return;

        let toastChildrenLength = children.length + 1;

        if (toastChildrenLength > TOAST_LIMIT) {
            for (let i = toastChildrenLength - 2; i >= TOAST_LIMIT+1; i--) {
                if(children[i] !== null){
                    removeToast(children[i]);
                }
            }
        }
    });
}

function showTooltip(tooltipIndicatorElement) {
    // Get tooltip
    let tooltip = $(tooltipIndicatorElement).siblings('.tooltip');
    // Get tooltip indicator position
    let tooltipIndicatorElementPos = tooltipIndicatorElement.getBoundingClientRect();

    // Get parent
    let parent = tooltipIndicatorElement.closest('.modal-body');
    let parentPos = parent ? parent.getBoundingClientRect() : {top: 0, left: 0};

    // Get window scroll
    let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    let scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;

    // Get modal scroll
    let modalScrollTop = parent ? parent.scrollTop : 0;

    let top = tooltipIndicatorElementPos.top + scrollTop + modalScrollTop - parentPos.top;
    // 8 = padding tooltip indicator (px)
    let left = tooltipIndicatorElementPos.left + scrollLeft - parentPos.left + $(tooltipIndicatorElement).width() + 8;
    $(tooltip).css({'top': top, 'left': left }).show();
}

function hideTooltop(tooltipIndicatorElement) {
    let tooltip = $(tooltipIndicatorElement).siblings('.tooltip');
    $(tooltip).hide();
}

function tooltip() {
    $(document).on({
        focusin: function (e) {
            if(e.target.classList.contains('tooltip-indicator')){
                showTooltip(e.target);
            }
        },

        focusout: function (e) {
            if (e.target.classList.contains('tooltip-indicator')) {
                hideTooltop(e.target);
            }
        },

        mouseenter: function (e) {
            if (e.target.classList.contains('tooltip-indicator')) {
                isTooltipIndicatorClicked = false;
                showTooltip(e.target);
            }
        },

        mouseleave: function (e) {
            if (e.target.classList.contains('tooltip-indicator')) {
                if (!$(e.target).is(":focus")) {
                    hideTooltop(e.target);
                }
            }
        }
    }, '.tooltip-indicator');

    $(window).on('scroll', function(){
        $('.tooltip').hide();
    });
}

var transitionEvent = whichTransitionEvent();
console.log(transitionEvent);

breadcrumb();
let listTableCheckbox = $('table.table-checkbox');
for (const tableCheckbox of listTableCheckbox) {
    checkboxTable($(tableCheckbox));
}
darkModeHandler();
listItemCheckbox(".list-item-model-a");
listItemCheckbox(".list-item-model-b");
listItemCheckbox(".list-item-model-c");
listItemCheckbox(".list-item-model-d");
listItemRowCollapse(".list-item-model-f");
pagination();
passwordHandler();
tabElement();
toastHandler();
tooltip();
