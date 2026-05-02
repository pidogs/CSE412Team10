const sortColumn = document.getElementById('sortColumn');
const sortDirection = document.getElementById('sortDirection');
const searchInput = document.getElementById('searchInput');
const tableScope = document.getElementById('tableScope');
const errorDiv = document.getElementById('error');
const tableBody = document.getElementById('tableBody');
const tableHead = document.getElementById('tableHead');

function escapeAttr(s) {
  return String(s)
      .replace(/&/g, '&amp;')
      .replace(/"/g, '&quot;')
      .replace(/</g, '&lt;');
}

function nameColumnIndex(description) {
  const idx = description.findIndex(c => String(c).toLowerCase() === 'name');
  return idx >= 0 ? idx : 0;
}

function modelCountColumnIndex(description) {
  const idx = description.findIndex(
      c => String(c).toLowerCase() === 'modelcount');
  return idx;
}

// Sort dropdown options per scope (until /columns?scope= is implemented server-side).
const SORT_COLUMNS_BY_SCOPE = {
  Model: ['AircraftName', 'VariantName', 'Range'],
  Aircraft: ['Name'],
  Manufacturer: ['Name', 'YearFounded', 'ModelCount'],
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
  // Default to a real column otherwise ASC/DESC is ignored
  sortColumn.value = cols[0];
}

tableScope.addEventListener('change', loadSortColumns);
loadSortColumns();

// Rerun query when sort options change
sortColumn.addEventListener('change', fetchData);
sortDirection.addEventListener('change', fetchData);

function fetchData() {
  // Build the query string with the current filter and sort settings
  const queryParams = new URLSearchParams();
  queryParams.set('scope', tableScope.value);
  queryParams.set('search', searchInput.value);
  queryParams.set('sort_col', sortColumn.value);
  queryParams.set('sort_dir', sortDirection.value);

  // Clear any previous error message
  errorDiv.style.display = 'none';
  errorDiv.textContent = '';

  // Show a loading message while waiting for the response
  const scope = tableScope.value;
  const loadingCols = scope === 'Manufacturer' ? 99 : 5;
  tableBody.innerHTML =
      '<tr><td colspan="' + loadingCols + '">Loading</td></tr>';

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

        const colCount = data.description.length;
        const extraManufacturerCol = scope === 'Manufacturer' ? 1 : 0;
        const totalCols = Math.max(colCount + extraManufacturerCol, 1);

        // Build the table header
        let headerHtml = '<tr>';
        for (let i = 0; i < data.description.length; i++) {
          headerHtml += '<th>' + data.description[i] + '</th>';
        }
        if (scope === 'Manufacturer') {
          headerHtml += '<th>Models</th>';
        }
        headerHtml += '</tr>';
        tableHead.innerHTML = headerHtml;

        // Build the table body
        if (data.data.length === 0) {
          tableBody.innerHTML =
              '<tr><td colspan="' + totalCols +
              '">No results found</td></tr>';
        } else {
          let bodyHtml = '';
          const mfrNameIdx =
              scope === 'Manufacturer' ? nameColumnIndex(data.description) : -1;
          const mfrModelCountIdx = scope === 'Manufacturer' ?
              modelCountColumnIndex(data.description) :
              -1;
          for (let i = 0; i < data.data.length; i++) {
            let row = data.data[i];
            bodyHtml += '<tr>';

            for (let j = 0; j < row.length; j++) {
              let cellValue = row[j];
              if (cellValue === null || cellValue === undefined) {
                cellValue = 'N/A';
              }
              bodyHtml += '<td>' + cellValue + '</td>';
            }

            if (scope === 'Manufacturer') {
              const rawName = row[mfrNameIdx];
              const safeName =
                  rawName !== null && rawName !== undefined ?
                  String(rawName) :
                  '';
              let modelCount = 0;
              if (mfrModelCountIdx >= 0 && row[mfrModelCountIdx] != null) {
                const n = Number(row[mfrModelCountIdx]);
                modelCount = Number.isFinite(n) ? n : 0;
              }
              const btnLabel = 'View models (' + modelCount + ')';
              bodyHtml +=
                  '<td><button type="button" class="manufacturer-models-btn"' +
                  (safeName ?
                      ' data-manufacturer="' + escapeAttr(safeName) + '"' :
                      '') +
                  (safeName ? '' : ' disabled') + '>' + btnLabel +
                  '</button></td>';
            }

            bodyHtml += '</tr>';
          }
          tableBody.innerHTML = bodyHtml;
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

function renderNestedResultTable(data) {
  if (!data.description || !data.data) return '<p>No data</p>';
  if (data.data.length === 0) {
    return '<p class="nested-caption">No models linked for this manufacturer.</p>';
  }
  let html = '<table><thead><tr>';
  for (let i = 0; i < data.description.length; i++) {
    html += '<th>' + data.description[i] + '</th>';
  }
  html += '</tr></thead><tbody>';
  for (let r = 0; r < data.data.length; r++) {
    html += '<tr>';
    for (let c = 0; c < data.data[r].length; c++) {
      let v = data.data[r][c];
      if (v === null || v === undefined) v = 'N/A';
      html += '<td>' + v + '</td>';
    }
    html += '</tr>';
  }
  html += '</tbody></table>';
  return html;
}

tableBody.addEventListener('click', function(e) {
  const btn = e.target.closest('.manufacturer-models-btn');
  if (!btn || btn.disabled) return;
  const manufacturerName = btn.getAttribute('data-manufacturer');
  if (!manufacturerName) return;

  const tr = btn.closest('tr');
  const next = tr.nextElementSibling;
  if (next && next.classList.contains('manufacturer-models-detail') &&
      next.dataset.mfr === manufacturerName) {
    next.remove();
    return;
  }

  const colCount = tr.cells.length;
  const detail = document.createElement('tr');
  detail.className = 'manufacturer-models-detail';
  detail.dataset.mfr = manufacturerName;
  const td = document.createElement('td');
  td.colSpan = colCount;
  td.textContent = 'Loading models…';
  detail.appendChild(td);
  tr.insertAdjacentElement('afterend', detail);

  const params = new URLSearchParams();
  params.set('name', manufacturerName);
  fetch('/manufacturer-models?' + params.toString())
      .then(function(response) {
        return response.json();
      })
      .then(function(data) {
        if (data.error) {
          td.textContent = data.error;
          return;
        }
        const caption = document.createElement('p');
        caption.className = 'nested-caption';
        caption.textContent = 'Models for "' + manufacturerName + '"';
        td.textContent = '';
        td.appendChild(caption);
        const wrap = document.createElement('div');
        wrap.innerHTML = renderNestedResultTable(data);
        td.appendChild(wrap.firstChild);
      })
      .catch(function(err) {
        td.textContent = 'Request failed: ' + err;
      });
});