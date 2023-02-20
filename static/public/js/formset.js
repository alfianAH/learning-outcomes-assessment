function addMoreForm(totalFormId) {
    $('#add-form').on('click', function(){
        const currentFormCount = $('.added-form').length; // + 1
        const copyEmptyFormEl = $('#empty-form').clone(true);

        copyEmptyFormEl.removeClass('hidden').addClass('added-form mb-3');
        copyEmptyFormEl.removeAttr('id');
        $(copyEmptyFormEl.children()[0]).attr('id', `form-${currentFormCount}`);
        
        copyEmptyFormEl.find('.form-control').attr('required', 'true');
        
        const regex = new RegExp('__prefix__', 'g');
        copyEmptyFormEl.html(copyEmptyFormEl.html().replace(regex, currentFormCount));

        $(totalFormId).val(currentFormCount + 1);
        // now add new empty form element to our html form
        $('#form-list').append(copyEmptyFormEl);
    });
}

function changeDeleteFieldValue(deleteFormId) {
    let canDeleteFieldValue = $(`#${deleteFormId}`).is(':checked');
    canDeleteFieldValue = !canDeleteFieldValue;
    return canDeleteFieldValue;
}

function deleteExistingForm(button, deleteFormId) {
    const formNumber = $(button).attr('data-delete');
    let canDeleteFieldValue = changeDeleteFieldValue(deleteFormId);
    $(`#${deleteFormId}`).attr('checked', canDeleteFieldValue);
    
    if (canDeleteFieldValue) {
        $(`#form-${formNumber}`).addClass('hidden');
        $(`#deleted-form-${formNumber}`).removeClass('hidden');
    }
}

function undoDeleteExistingForm(element, deleteFormId) {
    const formNumber = $(element).attr('data-delete');
    let canDeleteFieldValue = changeDeleteFieldValue(deleteFormId);
    $(`#${deleteFormId}`).attr('checked', canDeleteFieldValue);

    if(!canDeleteFieldValue){
        $(`#form-${formNumber}`).removeClass('hidden');
        $(`#deleted-form-${formNumber}`).addClass('hidden');
    }
}