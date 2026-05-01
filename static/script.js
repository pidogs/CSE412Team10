const sortColumn = document.getElementById('sortColumn');
const sortDirection = document.getElementById('sortDirection');
const searchInput = document.getElementById('searchInput');
const errorDiv = document.getElementById('error');

// Load columns on page load
fetch('/columns')
    .then(r => r.json())
    .then(cols => {
      cols.forEach(col => {
        const opt = document.createElement('option');
        opt.value = col;
        opt.textContent = col;
        sortColumn.appendChild(opt);
      });
    })
    .catch(err => {
      errorDiv.textContent = 'Failed to load columns: ' + err;
    });

function fetchData() {
  // Build the query string with the current filter and sort settings
  const queryParams = new URLSearchParams();
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