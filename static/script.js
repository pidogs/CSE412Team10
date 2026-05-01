const sortColumn = document.getElementById('sortColumn');
const sortDirection = document.getElementById('sortDirection');
const searchInput = document.getElementById('searchInput');
const tableScope = document.getElementById('tableScope');
const errorDiv = document.getElementById('error');

// Sort dropdown options per scope (until /columns?scope= is implemented server-side).
const SORT_COLUMNS_BY_SCOPE = {
  Model: ['AircraftName', 'VariantName', 'Range'],
  Aircraft: ['Name'],
  Manufacturer: ['Name', 'YearFounded'],
};

function loadSortColumns() {
  const cols = SORT_COLUMNS_BY_SCOPE[tableScope.value];
  if (!cols) return;
  sortColumn.innerHTML = '<option value="">No Sort</option>';
  cols.forEach(col => {
    const opt = document.createElement('option');
    opt.value = col;
    opt.textContent = col;
    sortColumn.appendChild(opt);
  });
}

tableScope.addEventListener('change', loadSortColumns);
loadSortColumns();

function fetchData() {
  // Build the query string with the current filter and sort settings
  const queryParams = new URLSearchParams();
  queryParams.set('scope', tableScope.value);
  queryParams.set('search', searchInput.value);
  queryParams.set('sort_col', sortColumn.value);
  queryParams.set('sort_dir', sortDirection.value);

  // Clear any previous error message
  errorDiv.textContent = '';

  // Show a loading message while waiting for the response
  document.getElementById('tableBody').innerHTML =
      '<tr><td colspan="5">Loading</td></tr>';

  // Send the request to the server
  fetch('/data?' + queryParams.toString())
      .then(function(response) {
        return response.json();
      })
      .then(function(data) {
        // If the server returned an error, show it and stop
        if (data.error) {
          errorDiv.textContent = data.error;
          return;
        }

        // Build the table header
        let headerHtml = '<tr>';
        for (let i = 0; i < data.description.length; i++) {
          headerHtml += '<th>' + data.description[i] + '</th>';
        }
        headerHtml += '</tr>';
        document.getElementById('tableHead').innerHTML = headerHtml;

        // Build the table body
        if (data.data.length === 0) {
          // No matching records
          document.getElementById('tableBody').innerHTML =
              '<tr><td colspan="5">No results found</td></tr>';
        } else {
          // Build a row for each record
          let bodyHtml = '';
          for (let i = 0; i < data.data.length; i++) {
            let row = data.data[i];
            bodyHtml += '<tr>';

            for (let j = 0; j < row.length; j++) {
              // Show "N/A" for empty or missing values
              let cellValue = row[j];
              if (cellValue === null || cellValue === undefined) {
                cellValue = 'N/A';
              }
              bodyHtml += '<td>' + cellValue + '</td>';
            }

            bodyHtml += '</tr>';
          }
          document.getElementById('tableBody').innerHTML = bodyHtml;
        }
      })
      .catch(function(err) {
        // Network or parsing error
        errorDiv.textContent = 'Request failed: ' + err;
      });
}

// Search on Enter key
searchInput.addEventListener('keypress', e => {
  if (e.key === 'Enter') fetchData();
});