function addMoreForm(totalFormId) {
    $('#add-form').on('click', function(e){
        const currentFormCount = $('.added-form').length; // + 1
        const copyEmptyFormEl = $('#empty-form').clone(true);

        copyEmptyFormEl.removeClass('hidden').addClass('added-form mb-3');
        copyEmptyFormEl.attr('id', `form-${currentFormCount}`);
        
        const regex = new RegExp('__prefix__', 'g');
        copyEmptyFormEl.html(copyEmptyFormEl.html().replace(regex, currentFormCount));

        $(totalFormId).val(currentFormCount + 1);
        // now add new empty form element to our html form
        $('#form-list').append(copyEmptyFormEl);
    });
}