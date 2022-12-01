const USER_ROLE_KEY = "user_role";

function checkForStorage() {
    return typeof(Storage) !== "undefined"
}

// Save user role when logging in
function userRoleHandler() {
    let userRoleField = $('#login-as');
    let userRoleValue = userRoleField.find(":selected").val();

    if (checkForStorage()) {
        let userRole = localStorage.getItem(USER_ROLE_KEY);

        if (userRole === null) {
            localStorage.setItem(USER_ROLE_KEY, userRoleValue);
        } else {
            $(userRoleField).val(userRole);
        }
    }

    userRoleField.on("change", function () {
        userRoleValue = userRoleField.find(":selected").val();
        localStorage.setItem(USER_ROLE_KEY, userRoleValue);
        
        switch (userRoleValue) {
            case 'mahasiswa':
                $('#admin-dosen').addClass('hidden');
                $('#mahasiswa').removeClass('hidden');
                break;
            case 'admin-dosen':
                $('#admin-dosen').removeClass('hidden');
                $('#mahasiswa').addClass('hidden');
                break;
            default:
                break;
        }
    }).trigger('change');
}

userRoleHandler();
