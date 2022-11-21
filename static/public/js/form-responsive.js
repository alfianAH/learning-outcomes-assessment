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
        let form = $(`#${formId}`);
        let selectedIndicatorLength = form.find('input:checkbox:checked').length;
        let selectedIndicator = form.siblings('.selected-indicator');
        let selectedIndicatorStatus = selectedIndicator.find('#selected-indicator-status');

        if (selectedIndicatorLength > 0) {
            $(selectedIndicator).removeClass('hidden');
            $(selectedIndicatorStatus).text(`${selectedIndicatorLength} item dipilih`);
        } else {
            $(selectedIndicator).addClass('hidden');
        }
    });
}