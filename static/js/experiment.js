document.addEventListener('DOMContentLoaded', function() {
    function attachRemoveRoleEvent(button) {
        button.addEventListener('click', function() {
            const table = document.getElementById('roles-sections-table');
            const headerRow = table.querySelector('thead tr');
            const index = Array.from(headerRow.children).indexOf(button.closest('th'));
            headerRow.removeChild(button.closest('th'));
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                // Remove the child only if it is not a shared section
                const sectionType = row.querySelector('.section-type').value;
                if (sectionType !== 'shared')
                    row.removeChild(row.children[index]);
            });
            //reconfigureSections();
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
            contentCell.innerHTML = `
                <textarea class="form-control content-column scrollable-content" name="section_content[]" placeholder="Content"></textarea>
            `;
            contentCell.classList.add('shared-cell');

            // Remove extra cells if any
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

    // Attach remove event to initial role remove button
    document.querySelectorAll('.remove-role').forEach(button => {
        attachRemoveRoleEvent(button);
    });

    // Attach remove event to initial section remove buttons
    document.querySelectorAll('.remove-section').forEach(button => {
        attachRemoveSectionEvent(button);
    });

    // Attach change event to initial section type selectors
    document.querySelectorAll('.section-type').forEach(select => {
        select.addEventListener('change', function() {
            const row = select.closest('tr');
            updateSectionContent(row, select.value);
        });
    });

    // Function to add a new role
    document.getElementById('add-role').addEventListener('click', function() {
        const table = document.getElementById('roles-sections-table');
        const headerRow = table.querySelector('thead tr');
        const roleCount = headerRow.children.length; // Updated here

        // Add new header cell for the role
        const newHeaderCell = document.createElement('th');
        newHeaderCell.innerHTML = `
            <div class="d-flex">
                <input type="text" class="form-control" name="roles[]" placeholder="Role ${roleCount}" required>
                <button type="button" class="btn btn-danger btn-sm ml-2 remove-role">Remove</button>
            </div>
        `;
        headerRow.appendChild(newHeaderCell);

        // Add new cell for each section row
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const sectionType = row.querySelector('.section-type').value;
            if (sectionType === 'shared') {
                const contentCell = row.querySelector('.content-cell');
                contentCell.colSpan = roleCount;
            } else {
                const newCell = document.createElement('td');
                newCell.className = 'content-cell';
                newCell.innerHTML = `
                    <textarea class="form-control content-column scrollable-content" name="section_content[]" placeholder="Content"></textarea>
                `;
                row.appendChild(newCell);
            }
        });

        // Attach remove event to the new button
        attachRemoveRoleEvent(newHeaderCell.querySelector('.remove-role'));
    });

    // Function to add a new section
    document.getElementById('add-section').addEventListener('click', function() {
        const table = document.getElementById('roles-sections-table');
        const tbody = table.querySelector('tbody');
        const sectionIndex = tbody.children.length;
        const roleCount = table.querySelector('thead tr').children.length - 1;  // Exclude the last header cell

        // Create new row for the section
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
            <td class="fixed-column">
                <div class="d-flex flex-column">
                    <input type="text" class="form-control mb-2" name="sections[]" placeholder="Section ${sectionIndex}" required>
                    <div class="d-flex align-items-center justify-content-between">
                        <select class="form-control section-type mr-2" name="section_type[]" style="width: 100px;">
                            <option value="private" selected>Private</option>
                            <option value="shared">Shared</option>
                        </select>
                        <button type="button" class="btn btn-danger btn-sm remove-section">Remove</button>
                    </div>
                </div>
            </td>
            ${'<td class="content-cell"><textarea class="form-control content-column scrollable-content" name="section_content[]" placeholder="Content"></textarea></td>'.repeat(roleCount)}  <!-- Updated here -->
        `;
        tbody.appendChild(newRow);

        // Attach remove event to the new button
        attachRemoveSectionEvent(newRow.querySelector('.remove-section'));

        // Attach change event to the new section type selector
        newRow.querySelector('.section-type').addEventListener('change', function() {
            updateSectionContent(newRow, this.value);
        });

        // Re-attach remove role event to all remove buttons
        document.querySelectorAll('.remove-role').forEach(button => {
            attachRemoveRoleEvent(button);
        });
    });

    reconfigureSections();
});
