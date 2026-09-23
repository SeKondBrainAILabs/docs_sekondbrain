/* Carry each column's heading down into its cells, so a table can stack on a
   phone and still say what every value means.

   Below 700px `style.css` turns tables into one card per row. A stacked cell
   with no heading beside it is a bare string — "off", "12", "no" — so each cell
   needs to carry its own label, and `td[data-label]::before` renders it.

   Doing that by hand would mean annotating 143 tables and remembering to do it
   again for every table added after. This reads the headings the table already
   has instead. It runs once, sets nothing that is already set, and touches no
   table without a header row.

   Without this file the tables still stack and still read in order — they just
   lose the little column labels. Nothing depends on it having run. */
(function () {
  var tables = document.querySelectorAll('table');
  for (var t = 0; t < tables.length; t++) {
    var table = tables[t];

    /* The tool tables stack already, with their own rules and no header row. */
    if (table.classList.contains('tools')) continue;

    var headRow = table.querySelector('thead tr') || table.querySelector('tr');
    if (!headRow) continue;
    var heads = headRow.querySelectorAll('th');
    if (!heads.length) continue;               /* headerless key/value table */

    var labels = [];
    for (var h = 0; h < heads.length; h++) {
      /* textContent, not innerHTML: a heading may hold <code> or a link, and
         this lands in a CSS `content: attr(...)` string, which is plain text. */
      labels.push((heads[h].textContent || '').trim());
    }

    var rows = table.querySelectorAll('tbody tr');
    if (!rows.length) rows = table.querySelectorAll('tr');

    for (var r = 0; r < rows.length; r++) {
      var cells = rows[r].children;
      /* A row that does not line up with the header — a spanning cell, a
         sub-heading row — is left alone rather than mislabelled. */
      if (cells.length !== labels.length) continue;

      /* Start at 1: the first cell is the row's subject and reads as the
         card's title, so a label above it would only repeat the obvious. */
      for (var c = 1; c < cells.length; c++) {
        var cell = cells[c];
        if (cell.tagName !== 'TD') continue;
        if (cell.hasAttribute('data-label')) continue;   /* hand-set wins */
        if (!labels[c]) continue;                        /* blank heading */
        cell.setAttribute('data-label', labels[c]);
      }
    }
  }
})();
