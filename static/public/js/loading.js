function showLoadingIndicator() {
    $('.loading-trigger').on('click', function () {
        // Showing loading card
        $('#loading-card').addClass('showing');
        
        // Show loading card
        $('#loading-card').one(transitionEvent, function () {
            $('#loading-card').removeClass('showing').addClass('show');
        });
    });
}

function hideLoadingIndicator() {
    // Hide loading card
    $('#loading-card').addClass('hiding');

    $('#loading-card').one(transitionEvent, function () {
        // Remove loading card's classses
        $('#loading-card').removeClass('hiding show');
    });
}

window.onunload = function () {
    hideLoadingIndicator();
}

showLoadingIndicator();
