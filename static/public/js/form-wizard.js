const FORM_WIZARD_PAGE_CLASS = ".form-wizard-page";
const FORM_WIZARD_CONTENT_CLASS = ".form-wizard-content";
const FORM_WIZARD_CONTENT_PARENT_CLASS = ".form-wizard-parent";
const FORM_TAGS = ["input", "textarea", "select"]
const FORM_CONTENT_PAGE_PATTERN = /#form-content-page-(\d+)/;

const REVEALED_CLASS = "revealed",
    ACTIVE_CLASS = "active",
    LATEST_CLASS = "latest";


/**
 * Validate form element in form parents
 * @param {*} element Form parents
 * @returns True, if form is valid. False, if form is not valid
 */
function validateForm(element) {
    for (const formTag of FORM_TAGS) {
        let formElements = $(element).find(formTag);
        if (formElements.length == 0) continue;
        
        for (const formElement of formElements) {
            // If form is valid, continue
            // TODO: validation
            if ($(formElement).val() !== "") {
                continue;
            } else { // Else, return false right away
                // TODO: focus and give warning
                return false;
            }
        }
    }

    // Return true after all of form elements are valid
    return true;
}

/**
 * Empty all form fields in form element
 * @param {element} element formElement
 */
function emptyAllForms(element) {
    for (const formTag of FORM_TAGS) {
        let formElements = $(element).find(formTag);
        if (formElements.length == 0) continue;
        
        switch (formTag) {
            case "input":
                for (const formElement of formElements) {
                    let inputType = $(formElement).attr("type");
                    if(inputType == null) continue;
                    
                    switch (inputType) {
                        case "text":
                        case "number":
                        case "password":
                            $(formElement).val('');
                            break;
                        case "radio":
                        case "checkbox":
                            if($(formElement).prop("checked")){
                                $(formElement).prop("checked", false);
                            }
                            break;
                        default:
                            console.error(`${inputType} is not in case`);
                            break;
                    }
                }
                break;
            case "textarea":
            case "select":
                for (const formElement of formElements) {
                    $(formElement).val("");
                }
                break;
            default:
                break;
        }
        for (const formElement of formElements) {
            $(formElement).val('');
        }
    }
}

/**
 * Filter target's form content ID and return page number
 * @param {string} targetFormContentId target's form content ID
 * @returns Page number
 */
function getPageNumber(targetFormContentId) {
    let regexResult = targetFormContentId.match(FORM_CONTENT_PAGE_PATTERN);

    if (regexResult.length <= 1) {
        console.error(regexResult);
        return;
    }

    return parseInt(regexResult[1]);
}

/**
 * Update page data in form wizard buttons
 * @param {integer} page page number
 * @param {element} button page navigation button
 * @param {integer} currentPage current page number
 * @param {element} submitBtn form submit button
 */
function updateFormWizardButton(page, button, currentPage, submitBtn) {
    let lastPage = $(FORM_WIZARD_CONTENT_PARENT_CLASS).children().length;

    // If previous page isn't available,
    if($(page).length == 0){
        // Hide the next button
        button.addClass("hidden");
        // Update data-target in next button
        button.attr("data-target", "");
    } else if ($(page).length == 1) {
        // Show previous button
        button.removeClass("hidden");
        // Update data-target in previous button
        button.attr("data-target", page);
    }

    if (currentPage == lastPage) {
        // Show the sync button
        submitBtn.removeClass("hidden");
    } else {
        submitBtn.addClass("hidden");
    }
}

function formWizard() {
    let nextBtn = $(".form-wizard-buttons > #next-btn");
    let prevBtn = $(".form-wizard-buttons > #prev-btn");
    let submitBtn = $(".form-wizard-buttons > #submit-btn");

    let formHasChanged = false;
    let submitted = false;
    
    $(document).on("change", ".form-wizard input, .form-wizard select, .form-wizard textarea", function (e) {
        formHasChanged = true;
    });

    $(function () { 
        // Show prompt before unload
        $(window).on("beforeunload", function (e) {
            const pageAccessedByReload = window.performance
                .getEntriesByType('navigation')
                .map((nav) => nav.type)
                .includes('reload');

            if (formHasChanged && !submitted && pageAccessedByReload) {
                var message = "You have not saved your changes.";
                if (e) {
                    e.returnValue = message;
                }
                return message;
            }
        });

        // Empty all forms when unload
        $(window).on("unload", function (e) {
            const pageAccessedByReload = window.performance
                .getEntriesByType('navigation')
                .map((nav) => nav.type)
                .includes('reload');
            
            if(pageAccessedByReload)
                emptyAllForms(".form-wizard");
        });
        
        $($(".form-wizard").parent()).on("submit", function () {
            $(window).off("beforeunload");
            submitted = true;
        });
    });

    // Form page on click
    $(FORM_WIZARD_PAGE_CLASS).on("click", function () {
        let targetFormContentId = $(this).attr("data-target");
        let targetForm = $(targetFormContentId);
        let targetFormPage = $(targetForm.attr("data-page"));
        let activeFormPage = $(".form-wizard > nav > ol").find(`${FORM_WIZARD_PAGE_CLASS}.active`);

        // If target form content hasn't revealed yet, return        
        if (((targetFormPage.hasClass(REVEALED_CLASS) && !targetFormPage.hasClass(ACTIVE_CLASS) && !targetFormPage.hasClass(LATEST_CLASS)) && 
            ((!activeFormPage.hasClass(REVEALED_CLASS) && activeFormPage.hasClass(LATEST_CLASS)) ||
                (activeFormPage.hasClass(REVEALED_CLASS) && !activeFormPage.hasClass(LATEST_CLASS)))) ||
            (!targetFormPage.hasClass(REVEALED_CLASS) && !targetFormPage.hasClass(ACTIVE_CLASS) && targetFormPage.hasClass(LATEST_CLASS) &&
            activeFormPage.hasClass(REVEALED_CLASS) && !activeFormPage.hasClass(LATEST_CLASS))
        ) {
            // If can move form, update button and pages
            if (moveForm(targetForm)) {
                let currentPage = getPageNumber(targetFormContentId);
                
                let previousPage = `#form-content-page-${currentPage - 1}`;
                let nextPage = `#form-content-page-${currentPage + 1}`;
                
                updateFormWizardButton(nextPage, nextBtn, currentPage, submitBtn);
                updateFormWizardButton(previousPage, prevBtn, currentPage, submitBtn);
            }
        }
    });

    // Next button handler
    nextBtn.on("click", function () {
        let targetFormContentId = $(this).attr("data-target");
        let targetForm = $(targetFormContentId);
        
        // If can move form, update button and pages
        if (moveForm(targetForm)) {
            let currentPage = getPageNumber(targetFormContentId);
            
            let previousPage = `#form-content-page-${currentPage - 1}`;
            let nextPage = `#form-content-page-${currentPage + 1}`;
            
            updateFormWizardButton(nextPage, nextBtn, currentPage, submitBtn);
            updateFormWizardButton(previousPage, prevBtn, currentPage, submitBtn);
        }
    });

    // Previous button handler
    prevBtn.on("click", function () {
        let targetFormContentId = $(this).attr("data-target");
        let targetForm = $(targetFormContentId);
        
        // If can move form, update button and pages
        if (moveForm(targetForm)) {
            let currentPage = getPageNumber(targetFormContentId);
            
            let previousPage = `#form-content-page-${currentPage - 1}`;
            let nextPage = `#form-content-page-${currentPage + 1}`;
            
            updateFormWizardButton(nextPage, nextBtn, currentPage, submitBtn);
            updateFormWizardButton(previousPage, prevBtn, currentPage, submitBtn);
        }
    });
}

/**
 * Move active form to the target form
 * @param {element} targetForm Target form element
 * @returns Returns true if can move to target form, false if cannot move to target form
 */
function moveForm(targetForm) {
    let activeForm = $(FORM_WIZARD_CONTENT_PARENT_CLASS).find(`${FORM_WIZARD_CONTENT_CLASS}.active`);

    let activeFormPage = $(".form-wizard > nav > ol").find(`${FORM_WIZARD_PAGE_CLASS}.active`);

    let isNext = false;

    let targetFormPage = $(targetForm.attr("data-page"));

    let activeIndex = $(FORM_WIZARD_CONTENT_CLASS).index(activeForm);
    let targetIndex = $(FORM_WIZARD_CONTENT_CLASS).index(targetForm);
    
    // Allow move to previous without validation
    if (targetIndex > activeIndex) {
        isNext = true;
    }

    let isActiveFormValid = validateForm(activeForm);

    // If form isn't valid, don't move and give warning
    if (!isActiveFormValid && isNext) {
        console.log("Form not valid");
        return false;
    }

    if (isActiveFormValid && isNext) {
        activeFormPage.addClass("revealed");
        activeFormPage.removeClass("latest");
    }

    if (!targetFormPage.hasClass("revealed")) {
        targetFormPage.addClass("latest");
    }

    // Deactivate active form content
    activeForm.removeClass("active");
    // Switch the active page to the clicked page
    activeFormPage.removeClass("active");
    targetFormPage.addClass("active");

    // Next content
    if (targetIndex > activeIndex) {
        // Context: ... active ... target
        // Content from active until target get disabled
        // Remove hidden to make numbering is still in order
        for (let i = activeIndex; i < targetIndex; i++){
            $(`#form-content-page-${i + 1}`).addClass("disabled").removeClass("hidden");
        }
        // Clicked content removes disabled and hidden
        targetForm.removeClass("disabled hidden");
    }

    // Fade out animation
    activeForm.find(".fade").removeClass("show");

    // Show the clicked form content
    targetForm.addClass("active");
    targetForm.find(".fade").removeClass("hidden").addClass("active");

    // After active form content fade out, ...
    activeForm.one(transitionEvent, function () {
        // Hide form content (because fade is only opacity)
        activeForm.find(".fade").addClass("hidden").removeClass("active");

        // Show clicked form content
        targetForm.find(".fade").addClass("show");

        // Previous content
        if (targetIndex < activeIndex) {
            for (let i = activeIndex; i > targetIndex; i--){
                $(`#form-content-page-${i + 1}`).addClass("hidden");
            }
            // Clicked content removes disabled
            targetForm.removeClass("disabled");
        }
    });

    return true;
}

formWizard();