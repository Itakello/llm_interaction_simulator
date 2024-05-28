document.addEventListener('DOMContentLoaded', function () {
    
    const MAX_ROLES = 5;
    const MAX_SECTIONS = 10;

    function attachRemoveRoleEvent(button) {
        button.addEventListener('click', function() {
            const table = document.getElementById('roles-sections-table');
            const headerRow = table.querySelector('thead tr');
            const index = Array.from(headerRow.children).indexOf(button.closest('th'));
            headerRow.removeChild(button.closest('th'));
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const sectionType = row.querySelector('.section-type').value;
                if (sectionType !== 'shared')
                    row.removeChild(row.children[index]);
            });
        });
    }

    function attachRemoveSectionEvent(button) {
        button.addEventListener('click', function() {
            button.closest('tr').remove();
        });
    }

    function updateSectionContent(row, type) {
        const roleCount = document.getElementById('roles-sections-table').querySelector('thead tr').children.length - 1;
        const contentCell = row.querySelector('.content-cell');
        contentCell.innerHTML = '';
        if (type === 'shared') {
            contentCell.colSpan = roleCount;
            contentCell.innerHTML = `<textarea class="form-control content-column scrollable-content" name="section_content[]" placeholder="Content"></textarea>`;
            contentCell.classList.add('shared-cell');
            let sibling = contentCell.nextElementSibling;
            while (sibling) {
                const nextSibling = sibling.nextElementSibling;
                sibling.remove();
                sibling = nextSibling;
            }
        } else {
            contentCell.colSpan = 1;
            contentCell.classList.remove('shared-cell');
            for (let i = 0; i < roleCount; i++) {
                const newContentCell = document.createElement('td');
                newContentCell.className = 'content-cell';
                newContentCell.innerHTML = `<textarea class="form-control content-column scrollable-content" name="section_content[]" placeholder="Content"></textarea>`;
                contentCell.parentNode.insertBefore(newContentCell, contentCell.nextSibling);
            }
            contentCell.remove();
        }
    }

    function reconfigureSections() {
        const rows = document.querySelectorAll('#roles-sections-table tbody tr');
        rows.forEach(row => {
            const sectionType = row.querySelector('.section-type').value;
            updateSectionContent(row, sectionType);
        });
    }

    document.querySelectorAll('.remove-role').forEach(button => {
        attachRemoveRoleEvent(button);
    });

    document.querySelectorAll('.remove-section').forEach(button => {
        attachRemoveSectionEvent(button);
    });

    document.querySelectorAll('.section-type').forEach(select => {
        select.addEventListener('change', function() {
            const row = select.closest('tr');
            updateSectionContent(row, select.value);
        });
    });

    document.getElementById('add-role').addEventListener('click', function() {
        const table = document.getElementById('roles-sections-table');
        const headerRow = table.querySelector('thead tr');
        const roleCount = headerRow.children.length;

        if (roleCount > MAX_ROLES) {
            alert(`You can only add up to ${MAX_ROLES} roles.`);
            return;
        }

        const newHeaderCell = document.createElement('th');
        newHeaderCell.innerHTML = `
            <div class="role-container d-flex justify-content-between align-items-center">
                <input type="text" class="form-control role-input" name="roles[]" placeholder="Role ${roleCount}" required>
                <button type="button" class="btn btn-danger btn-sm remove-role">Remove</button>
            </div>
        `;
        headerRow.appendChild(newHeaderCell);
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const sectionType = row.querySelector('.section-type').value;
            if (sectionType === 'shared') {
                const contentCell = row.querySelector('.content-cell');
                contentCell.colSpan = roleCount;
            } else {
                const newCell = document.createElement('td');
                newCell.className = 'content-cell';
                newCell.innerHTML = `<textarea class="form-control content-column scrollable-content" name="section_content[]" placeholder="Content"></textarea>`;
                row.appendChild(newCell);
            }
        });
        attachRemoveRoleEvent(newHeaderCell.querySelector('.remove-role'));
    });

    document.getElementById('add-section').addEventListener('click', function() {
        const table = document.getElementById('roles-sections-table');
        const tbody = table.querySelector('tbody');
        const sectionIndex = tbody.children.length;
        const roleCount = table.querySelector('thead tr').children.length - 1;

        if (sectionIndex >= MAX_SECTIONS+1) {
            alert(`You can only add up to ${MAX_SECTIONS} sections.`);
            return;
        }

        const newRow = document.createElement('tr');
        newRow.innerHTML = `
            <td class="fixed-column">
                <div class="d-flex flex-column">
                    <input type="text" class="form-control mb-2 section-input" name="sections[]" placeholder="Section ${sectionIndex}" required>
                    <div class="d-flex align-items-center justify-content-between">
                        <select class="form-control section-type mr-2" name="section_type[]" style="width: 100px;">
                            <option value="private" selected>Private</option>
                            <option value="shared">Shared</option>
                        </select>
                        <button type="button" class="btn btn-danger btn-sm remove-section">Remove</button>
                    </div>
                </div>
            </td>
            ${'<td class="content-cell"><textarea class="form-control content-column scrollable-content" name="section_content[]" placeholder="Content"></textarea></td>'.repeat(roleCount)}
        `;
        tbody.appendChild(newRow);
        attachRemoveSectionEvent(newRow.querySelector('.remove-section'));
        newRow.querySelector('.section-type').addEventListener('change', function() {
            updateSectionContent(newRow, this.value);
        });
    });

    reconfigureSections();
});

document.querySelector('form').addEventListener('submit', function(event) {
        const table = document.getElementById('roles-sections-table');
        const roles = [];
        const sections = [];

        table.querySelectorAll('thead tr th').forEach((header, index) => {
            const roleInput = header.querySelector('.role-input');
            if (roleInput) {
                const role = { name: roleInput.value, sections: [] };
                table.querySelectorAll('tbody tr').forEach(row => {
                    const sectionType = row.querySelector('.section-type').value;
                    if (sectionType === 'private') {
                        const sectionContent = row.querySelectorAll('.content-column')[index - 1].value;
                        role.sections.push({
                            index: Array.from(row.parentNode.children).indexOf(row),
                            title: row.querySelector('.section-input').value,
                            content: sectionContent,
                            role: role.name
                        });
                    }
                });
                roles.push(role);
            }
        });

        table.querySelectorAll('tbody tr').forEach(row => {
            const sectionType = row.querySelector('.section-type').value;
            if (sectionType === 'shared') {
                sections.push({
                    index: Array.from(row.parentNode.children).indexOf(row),
                    title: row.querySelector('.section-input').value,
                    content: row.querySelector('.content-column').value
                });
            }
        });

        const data = {
            creator: document.getElementById('creator').value,
            starting_message: document.getElementById('starting_message').value,
            llms: Array.from(document.getElementById('llms').selectedOptions).map(option => option.value),
            note: document.getElementById('note').value,
            favourite: document.getElementById('favourite').checked,
            roles: roles,
            sections: sections
        };

        document.getElementById('serialized-data').value = JSON.stringify(data);
    });

