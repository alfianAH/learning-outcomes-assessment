function addMoreForm(totalFormId) {
    $('#add-form').on('click', function(){
        const currentFormCount = $('.added-form').length; // + 1
        const copyEmptyFormEl = $('#empty-form').clone(true);

        copyEmptyFormEl.removeClass('hidden').addClass('added-form mb-3');
        copyEmptyFormEl.attr('id', `form-${currentFormCount}`);
        
        copyEmptyFormEl.find('.form-control').attr('required', 'true');
        
        const regex = new RegExp('__prefix__', 'g');
        copyEmptyFormEl.html(copyEmptyFormEl.html().replace(regex, currentFormCount));

        $(totalFormId).val(currentFormCount + 1);
        // now add new empty form element to our html form
        $('#form-list').append(copyEmptyFormEl);
    });
}

function deleteForm(button, totalFormId) {
    // Delete form
    const formNumber = $(button).attr('data-delete');
    $(`#form-${formNumber}`).remove();

    // Update total form
    const currentFormCount = $('.added-form').length;
    $(totalFormId).val(currentFormCount);
}