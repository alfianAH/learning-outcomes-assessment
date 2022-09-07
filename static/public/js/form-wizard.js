const FORM_WIZARD_PAGE_CLASS = ".form-wizard-page";
const FORM_WIZARD_CONTENT_CLASS = ".form-wizard-content";
const FORM_WIZARD_CONTENT_PARENT_CLASS = ".form-wizard-parent";
const FORM_CONTENT_PAGE_PATTERN = /#form-content-page-(\d+)/;

const REVEALED_CLASS = "revealed",
    ACTIVE_CLASS = "active",
    LATEST_CLASS = "latest";

/**
 * Actions if form is invalid
 * @param {element} formError Form error element
 * @param {string} invalidMessage Invalid message
 * @param {element} formElement Form element
 */
function formInvalidActions(formError, invalidMessage, formElement = null) {
    // Add danger class to form element that has border
    if(formElement != null){
        // Change the field style
        $(formElement).addClass("danger");
    }
        
    // Show the warning
    $(formError).addClass("active");
    $(formError).text(invalidMessage);
}

/**
 * Actions if form is valid
 * @param {element} formError Form error element
 * @param {element} formElement Form element
 */
function formValidActions(formError, formElement = null) {
    // Remove danger class to form element that has border
    if(formElement != null){
        // Change the field style
        $(formElement).removeClass("danger");
    }
        
    // Hide the warning
    $(formError).removeClass("active");
}

/**
 * Validate if field is empty or not
 * @param {element} formElement Form element
 * @param {string} invalidMessage Invalid message
 * @returns Returns false if text field is empty, otherwise true
 */
function validateEmptyField(formElement, invalidMessage) {
    if ($(formElement).val() != "") return true;
    
    formInvalidActions($(formElement).siblings(".form-error"), invalidMessage, formElement);
    return false;
}

/**
 * Validate max length of text field
 * @param {element} formElement Form element
 * @returns Returns true if value doesn't exceed the max length, otherwise false
 */
function validateMaxLengthTextField(formElement) {
    let formError = $(formElement).siblings(".form-error");
    let limitChar = $(formElement).attr("maxlength");

    if (limitChar == null) return true;
    
    limitChar = parseInt(limitChar);
    if ($(formElement).val().length < limitChar) return true;

    formInvalidActions(formError, `Batas karakter: ${limitChar}`, formElement);
    return false;
}

/**
 * Validate text field
 * @param {element} formElement Form element
 * @returns Returns true if text field is filled and not exceed the max length, otherwise false
 */
function validateTextField(formElement) {
    let formError = $(formElement).siblings(".form-error");

    // If empty field, return false
    let isFieldFilled = validateEmptyField(formElement, "Field ini tidak boleh kosong");
    if (!isFieldFilled) return false;

    // If value exceeds the max length, return false
    let isFieldBelowMax = validateMaxLengthTextField(formElement);
    if (!isFieldBelowMax) return false;

    formValidActions(formError, formElement);
    return true;
}

/**
 * Validate number field if it has min or max attribute
 * @param {element} formElement Form element
 * @param {string} type min or max
 * @returns Returns true if number type is null or the value is in min until max range, otherwise false
 */
function validateMinMaxNumberField(formElement, type) {
    let formError = $(formElement).siblings(".form-error");
    let numberType = $(formElement).attr(type);

    if (numberType == null) return true;

    numberType = parseInt(numberType);

    switch (type) {
        case "min":
            if ($(formElement).val() < numberType) {
                formInvalidActions(formError, `Angka tidak boleh lebih kecil dari ${numberType}`, formElement);
                return false;
            }
            break;
        case "max":
            if ($(formElement).val() > numberType) {
                formInvalidActions(formError, `Angka tidak boleh lebih besar dari ${numberType}`, formElement);
                return false;
            }
            break;
        default:
            break;
    }

    return true;
}

/**
 * Validate number field
 * @param {element} formElement Form element
 * @returns Returns true if number is in range and valid number, otherwise false
 */
function validateNumberField(formElement) {
    let formError = $(formElement).siblings(".form-error");

    // If empty field, return false
    if (!validateEmptyField(formElement, "Field ini tidak valid")) {
        return false;
    }

    // Check min and max attribute
    let min = validateMinMaxNumberField(formElement, "min");
    let max = validateMinMaxNumberField(formElement, "max");

    // If all true then form is valid
    if (min && max) {
        formValidActions(formError, formElement);
        return true;
    }
}

/**
 * Validate select field
 * @param {element} formElement Form Element
 * @returns Returns true if user select an option that has value, otherwise false
 */
function validateSelectField(formElement) {
    let options = $(formElement).find("option:selected");

    if (options.length == 1) {
        let optionValue = $(options[0]).attr("value");
        // Return true if value is not empty string
        if (optionValue != "") {
            formValidActions($(formElement).siblings(".form-error"), formElement);
            return true;
        }
    }
    // Return false if option value is empty string and none are selected
    formInvalidActions($(formElement).siblings(".form-error"), "Pilih salah satu", formElement);
    return false;
}

/**
 * Validate radio field
 * @param {string} formFieldName Radio form field name
 * @param {*} formGroup Radios' group
 * @param {*} invalidMessage Invalid message if not valid
 * @returns Returns true if checked checkbox is 1, otherwise false
 */
function validateRadioField(formFieldName, formGroup, invalidMessage) {
    let formFields = $(`input[type='radio'][name='${formFieldName}']:checked`);

    if (formFields.length == 1) {
        formValidActions($(formGroup).find(".form-error"));
        return true;
    }

    formInvalidActions($(formGroup).find(".form-error"), invalidMessage);
    return false;
}

/**
 * Validate checkbox field
 * @param {string} formFieldName Checkbox form field name
 * @param {element} formGroup Checkboxes' group
 * @param {string} checkType Checkbox type. Value: "min", "max"
 * @param {integer} checkRequirement Checkbox that should be checked
 * @returns Returns true if it fits with criteria, false if doesn't fit
 */
function validateCheckboxField(formFieldName, formGroup, checkType="min", checkRequirement=0) {
    let formFields = $(`input[type='checkbox'][name='${formFieldName}']:checked`);
    let formError = $(formGroup).find(".form-error");

    switch (checkType) {
        case "min":
            if (formFields.length < checkRequirement) {
                formInvalidActions(formError,`Minimal pilihan: ${checkRequirement}`);
                return false;
            }
            break;
        case "max":
            if (formFields.length > checkRequirement) {
                formInvalidActions(formError,`Maksimal pilihan: ${checkRequirement}`);
                return false;
            }
            break;
        case "same":
            if (formFields.length != checkRequirement) {
                formInvalidActions(formError,`Harus memilih ${checkRequirement} pilihan.`);
                return false;
            }
        default:
            break;
    }

    formValidActions(formError);
    return true;
}

/**
 * Get array checked form field's name
 * @param {Array} formElements Array of check form fields
 * @returns Array of checked form field's name
 */
function getCheckedFieldNames(formElements) {
    let fieldNames = [];

    for (const formElement of formElements) {
        let fieldName = $(formElement).attr("name");

        if (!fieldNames.includes(fieldName)) {
            fieldNames.push(fieldName);
        }
    }

    return fieldNames;
}

/**
 * Validate form element in form parents
 * @param {*} element Form parents
 * @returns True, if form is valid. False, if form is not valid
 */
function validateForm(element) {
    let isValid = true;

    let textFieldElements = $(element).find("input[type=email][required], input[type=text][required], input[type=password][required], textarea[required]");
    let numberFieldElements = $(element).find("input[type=number][required]");
    let selectFieldElements = $(element).find("select[required]");
    let radioFieldElements = $(element).find("input[type='radio'][required]");
    let checkboxFieldElements = $(element).find("input[type='checkbox'][required]");

    if (textFieldElements.length > 0) {
        for (const formElement of textFieldElements) {
            if (!validateTextField(formElement, "Field ini tidak boleh kosong")) {
                isValid = false;
                // Focus on element
                $(formElement).triggerHandler("focus");
            }
        }
    }

    if (numberFieldElements.length > 0) {
        for (const formElement of numberFieldElements) {
            if (!validateNumberField(formElement)) {
                isValid = false;
                // Focus on element
                $(formElement).triggerHandler("focus");
            }
        }
    }

    if (selectFieldElements.length > 0) {
        for (const formElement of selectFieldElements) {
            if (!validateSelectField(formElement)) {
                isValid = false;
                // Focus on element
                $(formElement).triggerHandler("focus");
            }
        }
    }

    if (radioFieldElements.length > 0) {
        let radioFieldNames = getCheckedFieldNames(radioFieldElements);

        for (const radioFieldName of radioFieldNames) {
            // Get form group
            let radioGroup = $(`input[type='radio'][name='${radioFieldName}']`).closest(".form-group");

            let isRadioFieldValid = validateRadioField(radioFieldName, radioGroup, "Pilih salah satu");
            
            if (!isRadioFieldValid) {
                isValid = false;
                radioGroup.triggerHandler("focus");
            }
        }
    }

    if (checkboxFieldElements.length > 0) {
        let checkboxFieldNames = getCheckedFieldNames(checkboxFieldElements);

        for (const checkboxFieldName of checkboxFieldNames) {
            // Get form group
            let checkboxGroup = $(`input[type='checkbox'][name='${checkboxFieldName}']`).closest(".form-group");

            // Get check type and requirement
            let checkType = $(checkboxGroup).attr("data-checkbox-check-type");
            let checkRequirement = parseInt($(checkboxGroup).attr("data-checkbox-check-requirement"));

            let isCheckboxFieldValid = validateCheckboxField(checkboxFieldName, checkboxGroup, checkType, checkRequirement);

            if (!isCheckboxFieldValid) {
                isValid = false;
                checkboxGroup.triggerHandler("focus");
            }
        }
    }

    // Return true after all of form elements are valid
    return isValid;
}

/**
 * Empty all form fields in form element
 * @param {element} element formElement
 */
function emptyAllForms(element) {
    let valueFieldElements = $(element).find("input[type=email], input[type=text], input[type=password], input[type=number], textarea, select");
    let checkedFieldElements = $(element).find("input[type='radio'], input[type='checkbox']");

    if (valueFieldElements.length > 0) {
        for (const formElement of valueFieldElements) {
            $(formElement).val('');
        }
    }

    if (checkedFieldElements.length > 0) {
        for (const formElement of checkedFieldElements) {
            if($(formElement).prop("checked")){
                $(formElement).prop("checked", false);
            }
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

formWizard();