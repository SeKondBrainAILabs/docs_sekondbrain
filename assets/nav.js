/* Courtesies the checkbox-driven mobile menu cannot provide on its own.
   Everything works without this file — it only closes the panel at the two
   moments a reader expects it to close itself. */
document.addEventListener('click', function (e) {
  var t = document.getElementById('nav-toggle');
  if (t && t.checked && e.target.closest('.top-links a')) t.checked = false;
});
document.addEventListener('keydown', function (e) {
  var t = document.getElementById('nav-toggle');
  if (e.key === 'Escape' && t && t.checked) t.checked = false;
});
