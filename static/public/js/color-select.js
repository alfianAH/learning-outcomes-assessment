function colorSelect(selectId) {
    let options = $(selectId).children();
    let optionColors = [];
    for (const option of options) {
        optionColors.push($(option).attr('data-color'));
    }

    $(selectId).on('change', function () {
        let selectedColor = $(this).find(':selected').attr('data-color');
        let color = $(this).siblings('#color-result');
        
        for (const optionColor of optionColors) {
            if (color.hasClass(optionColor)) {
                color.removeClass(optionColor);
                break;
            }
        }

        color.addClass(selectedColor);
    }).trigger('change');
}