function onCheckboxChange(element, isChecked, closestSelector){
    // Check property
    $(element).prop('checked', isChecked);
    let closestElement = $(element).closest(closestSelector);

    // Add or remove active class
    if(isChecked){
        $(closestElement).addClass('active');
    } else{
        $(closestElement).removeClass('active');
    }
}

function onCheckboxClick(formId, listItemModel){
    $("input:checkbox").on("change", function () {
        let id = $(this).attr('id');
        let isChecked = $(this).prop('checked');
        
        let listInputElement = $(`ol#${formId}`).find(`#${id}`);
        let tableInputElement = $(`table#${formId}`).find(`#${id}`);

        onCheckboxChange(listInputElement, isChecked, listItemModel);
        onCheckboxChange(tableInputElement, isChecked, 'tr');
        
        // Update selected indicator
        let selectedIndicatorLength = $(`#${formId}`).find('input:checkbox:checked').length;

        if (selectedIndicatorLength > 0) {
            $('.selected-indicator').removeClass('hidden');
            $('#selected-indicator-status').text(`${selectedIndicatorLength} item dipilih`);
        } else {
            $('.selected-indicator').addClass('hidden');
        }
    });
}