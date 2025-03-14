function openUserEditForm(userId, firstName, lastName, phone, birthDate, isAdmin) {
    document.getElementById('edit-user-id').value = userId;
    document.getElementById('edit-first-name').value = firstName;
    document.getElementById('edit-last-name').value = lastName;
    document.getElementById('edit-phone').value = phone;
    document.getElementById('edit-birth-date').value = birthDate;
    document.getElementById('edit-role').value = isAdmin;
    document.getElementById('reset-password').value = '';
    document.getElementById('reset-password-check').checked = false;
    document.getElementById('user-edit-form').style.display = 'block';
}

document.getElementById('reset-password-check').addEventListener('change', function() {
    document.getElementById('reset-password').disabled = !this.checked;
});
     
function closeUserEditForm() {
    document.getElementById('user-edit-form').style.display = 'none';
}