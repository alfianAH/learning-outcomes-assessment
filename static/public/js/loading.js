function showLoadingIndicator() {
    // Showing loading card
    $('#loading-card').addClass('showing');
        
    // Show loading card
    $('#loading-card').one(transitionEvent, function () {
        $('#loading-card').removeClass('showing').addClass('show');
    });
}

function loadingIndicatorListener() {
    $('.loading-trigger').on('click', function () {
        showLoadingIndicator();
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

function confirmDelete() {
    $('.confirmation').on('click', function () {
        let confirmMessage = $(this).attr('data-confirm');
        
        if (confirmMessage == null) {
            confirmMessage = 'Apakah anda yakin?'
        }
        
        if (confirm(confirmMessage)) {
            showLoadingIndicator();
            return true;
        } else {
            return false;
        }
    });
}

window.onunload = function () {
    hideLoadingIndicator();
}

confirmDelete();
loadingIndicatorListener();
