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

function onCheckboxClick(formId){
    $("input:checkbox").on("change", function () {
        let id = $(this).attr('id');
        let isChecked = $(this).prop('checked');
        
        let listInputElement = $(`ol#${formId}`).find(`#${id}`);
        let tableInputElement = $(`table#${formId}`).find(`#${id}`);

        onCheckboxChange(listInputElement, isChecked, '.list-item-model-a');
        onCheckboxChange(tableInputElement, isChecked, 'tr');
    });
}