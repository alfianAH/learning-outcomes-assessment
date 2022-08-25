const FORM_WIZARD_PAGE_CLASS = ".form-wizard-page";
const FORM_WIZARD_CONTENT_CLASS = ".form-wizard-content";
const FORM_TAGS = ["input", "textarea", "select"]
const FORM_CONTENT_PAGE_PATTERN = /#form-content-page-(\d+)/;

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
            if ($(formElement).val() !== "") {
                continue;
            } else { // Else, return false right away
                return false;
            }
        }
    }

    // Return true after all of form elements are valid
    return true;
}

function formWizard() {
    let nextBtn = $(".form-wizard-buttons > #next-btn");
    let prevBtn = $(".form-wizard-buttons > #prev-btn");
    let submitBtn = $(".form-wizard-buttons > #submit-btn");

    // Form page on click
    $(FORM_WIZARD_PAGE_CLASS).on("click", function () {
        let targetFormContentId = $(this).attr("data-target");
        let targetForm = $(targetFormContentId);
        let targetFormPage = $(targetForm.attr("data-page"));

        // If target form content doesn't have active or revealed class, return
        if (!targetFormPage.hasClass("revealed")) return;
        
        moveForm(targetForm);
    });

    // Next button handler
    nextBtn
        .on("click", function () {
            let targetFormContentId = $(this).attr("data-target");
            let targetForm = $(targetFormContentId);
            
            // If can move form, ...
            if (moveForm(targetForm)) {
                let regexResult = targetFormContentId.match(FORM_CONTENT_PAGE_PATTERN);

                if (regexResult.length <= 1) {
                    console.log(regexResult);
                    return;
                }
                let currentPage = parseInt(regexResult[1]);
                
                let previousPage = `#form-content-page-${currentPage - 1}`;
                let nextPage = `#form-content-page-${currentPage + 1}`;
                
                // If previous page is available,
                if ($(previousPage).length == 1) {
                    // Show previous button
                    prevBtn.removeClass("hidden");
                    // Update data-target in previous button
                    prevBtn.attr("data-target", previousPage);
                }
                
                // If next page isn't available, 
                if($(nextPage).length == 0){
                    // Hide the next button
                    $(this).addClass("hidden");
                    // Update data-target in next button
                    $(this).attr("data-target", "");
                    // Show the sync button
                    $(submitBtn).removeClass("hidden");
                } else if ($(nextPage).length == 1) {
                    // Show the next button
                    $(this).removeClass("hidden");
                    // Update data-target in next button
                    $(this).attr("data-target", nextPage);
                }
            }
        }).end()
        .on("change", function () {
            let targetFormContentId = $(this).attr("data-target");
            console.log("next change");
            if (targetFormContentId == null) {
                console.log("next hide");
                $(this).addClass("hidden");
            } else {
                console.log("next show");
                $(this).removeClass("hidden");
            }
        }).trigger("change").end();

    // Previous button handler
    prevBtn
        .on("click", function () {
            let targetFormContentId = $(this).attr("data-target");
            let targetForm = $(targetFormContentId);
            
            // If can move form, ...
            if (moveForm(targetForm)) {
                let regexResult = targetFormContentId.match(FORM_CONTENT_PAGE_PATTERN);

                if (regexResult.length <= 1) {
                    console.log(regexResult);
                    return;
                }
                let currentPage = parseInt(regexResult[1]);
                
                let previousPage = `#form-content-page-${currentPage - 1}`;
                let nextPage = `#form-content-page-${currentPage + 1}`;
                
                // If next page is available,
                if ($(nextPage).length == 1) {
                    // Show next button
                    nextBtn.removeClass("hidden");
                    // Update data-target in next button
                    nextBtn.attr("data-target", nextPage);
                }
                
                // If previous page isn't available, 
                if ($(previousPage).length == 0) {
                    // Hide the previous button
                    $(this).addClass("hidden");
                    // Update data-target in previous button
                    $(this).attr("data-target", "");
                } else if ($(previousPage).length == 1) {
                    // Show the previous button
                    $(this).removeClass("hidden");
                    // Update data-target in previous button
                    $(this).attr("data-target", previousPage);
                }
            }
        }).end()
        .on("change", function () {
            let targetFormContentId = $(this).attr("data-target");
            console.log("previous change");
            if (targetFormContentId == null) {
                console.log("previous hide");
                $(this).addClass("hidden");
            } else {
                console.log("previous show");
                $(this).removeClass("hidden");
            }
        }).trigger("change").end();
}

function moveForm(targetForm) {
    let formContentsParent = $(FORM_WIZARD_CONTENT_CLASS).parent();
    let activeFormPage = $(".form-wizard > nav > ol").find(`${FORM_WIZARD_PAGE_CLASS}.active`);
    let activeForm = formContentsParent.find(`${FORM_WIZARD_CONTENT_CLASS}.active`);

    let isNext = false;

    let targetFormPage = $(targetForm.attr("data-page"));

    let activeIndex = $(FORM_WIZARD_CONTENT_CLASS).index(activeForm);
    let targetIndex = $(FORM_WIZARD_CONTENT_CLASS).index(targetForm);
    
    // Allow move to previous without validation
    if (targetIndex > activeIndex) {
        isNext = true;
    }

    // If form isn't valid, don't move and give warning
    if (!validateForm(activeForm) && isNext) {
        console.log("Form not valid");
        return false;
    }

    // Deactivate active form content
    activeForm.removeClass("active");
    // Switch the active page to the clicked page
    // if (!activeFormPage.hasClass("revealed"))
    activeFormPage.addClass("revealed");
    activeFormPage.removeClass("active");
    targetFormPage.addClass("active");

    if (targetIndex > activeIndex) {
        // Context: ... active ... clicked
        // Content from clicked until active + 1 goes disabled
        activeForm.addClass("disabled");
        // Clicked content removes hidden
        targetForm.removeClass("hidden");
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
        if(targetIndex < activeIndex) {
            // Acitve goes hidden
            activeForm.addClass("hidden");
            // Clicked content removes disabled
            targetForm.removeClass("disabled");
        }
    });

    return true;
}

formWizard();