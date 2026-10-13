/**
 * CINEVERSE - Main Interactive Scripts
 * Handles star review selection, tooltip/popover init, and alert interactions.
 */

document.addEventListener('DOMContentLoaded', function () {
  // Star rating interactive selector for reviews
  const starInputs = document.querySelectorAll('.star-rating-widget input[type="radio"]');
  const ratingFeedback = document.getElementById('selectedRatingFeedback');

  if (starInputs.length > 0) {
    const ratingLabels = {
      '5': '★★★★★ (5/5) Masterpiece!',
      '4': '★★★★☆ (4/5) Great Movie',
      '3': '★★★☆☆ (3/5) Good / Decent',
      '2': '★★☆☆☆ (2/5) Disappointing',
      '1': '★☆☆☆☆ (1/5) Poor'
    };

    starInputs.forEach(input => {
      input.addEventListener('change', function () {
        if (ratingFeedback && ratingLabels[this.value]) {
          ratingFeedback.textContent = ratingLabels[this.value];
        }
      });
    });
  }

  // Auto-dismiss alerts after 6 seconds
  const autoAlerts = document.querySelectorAll('.alert-dismissible');
  autoAlerts.forEach(alertEl => {
    setTimeout(() => {
      if (window.bootstrap && bootstrap.Alert) {
        const bsAlert = new bootstrap.Alert(alertEl);
        bsAlert.close();
      }
    }, 6000);
  });
});
