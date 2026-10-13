/**
 * CINEVERSE - Interactive 5x8 Seat Booking Matrix
 * Handles seat selection, real-time ticket price calculation, and form synchronization.
 */

document.addEventListener('DOMContentLoaded', function () {
  const seatGrid = document.getElementById('seatGrid');
  const selectedSeatsInput = document.getElementById('selectedSeatsInput');
  const selectedSeatsDisplay = document.getElementById('selectedSeatsDisplay');
  const seatCountDisplay = document.getElementById('seatCountDisplay');
  const ticketBasePriceSpan = document.getElementById('ticketBasePrice');
  const totalPriceDisplay = document.getElementById('totalPriceDisplay');
  const bookingForm = document.getElementById('seatBookingForm');
  const checkoutBtn = document.getElementById('checkoutBtn');
  const validationAlert = document.getElementById('seatSelectionAlert');

  if (!seatGrid) return;

  // Read base price from data attribute or fallback
  const basePrice = parseFloat(seatGrid.dataset.ticketPrice || '12.50');
  
  // Set of selected seats (e.g. 'A1', 'B4')
  let selectedSeats = new Set();

  // Parse existing selected seats if any (e.g. on validation re-render)
  if (selectedSeatsInput && selectedSeatsInput.value) {
    const initialSeats = selectedSeatsInput.value.split(',').map(s => s.trim().toUpperCase()).filter(Boolean);
    initialSeats.forEach(seat => {
      const seatEl = seatGrid.querySelector(`[data-seat="${seat}"]`);
      if (seatEl && !seatEl.classList.contains('booked')) {
        seatEl.classList.add('selected');
        selectedSeats.add(seat);
      }
    });
    updateBookingSummary();
  }

  // Handle seat clicks using event delegation
  seatGrid.addEventListener('click', function (e) {
    const seatEl = e.target.closest('.seat-item');
    if (!seatEl) return;

    // Ignore if already booked
    if (seatEl.classList.contains('booked')) {
      showToast('This seat is already booked for this showtime.', 'warning');
      return;
    }

    const seatCode = seatEl.dataset.seat;
    if (!seatCode) return;

    if (seatEl.classList.contains('selected')) {
      seatEl.classList.remove('selected');
      selectedSeats.delete(seatCode);
    } else {
      seatEl.classList.add('selected');
      selectedSeats.add(seatCode);
    }

    updateBookingSummary();
  });

  // Function to recalculate and refresh UI
  function updateBookingSummary() {
    const sortedSeats = Array.from(selectedSeats).sort();
    const count = sortedSeats.length;
    const total = (count * basePrice).toFixed(2);

    // Sync with hidden input for Django form
    if (selectedSeatsInput) {
      selectedSeatsInput.value = sortedSeats.join(', ');
    }

    // Update Seat Count display
    if (seatCountDisplay) {
      seatCountDisplay.textContent = count === 1 ? '1 seat' : `${count} seats`;
    }

    // Update Selected Seats chip list
    if (selectedSeatsDisplay) {
      if (count === 0) {
        selectedSeatsDisplay.innerHTML = '<span class="text-muted fst-italic">No seats selected yet</span>';
      } else {
        selectedSeatsDisplay.innerHTML = sortedSeats
          .map(seat => `<span class="badge bg-warning text-dark me-1 mb-1 px-2 py-1 fs-6"><i class="bi bi-ticket-fill me-1"></i>${seat}</span>`)
          .join('');
      }
    }

    // Update Total Price display
    if (totalPriceDisplay) {
      totalPriceDisplay.textContent = `$${total}`;
    }

    // Update Checkout Button State
    if (checkoutBtn) {
      checkoutBtn.disabled = count === 0;
      if (count > 0) {
        checkoutBtn.innerHTML = `<i class="bi bi-shield-check me-2"></i>Confirm & Pay $${total}`;
      } else {
        checkoutBtn.innerHTML = `<i class="bi bi-hand-index-thumb me-2"></i>Select Seats to Proceed`;
      }
    }

    // Hide validation alert if seats are chosen
    if (validationAlert && count > 0) {
      validationAlert.classList.add('d-none');
    }
  }

  // Form submission validation
  if (bookingForm) {
    bookingForm.addEventListener('submit', function (e) {
      if (selectedSeats.size === 0) {
        e.preventDefault();
        if (validationAlert) {
          validationAlert.classList.remove('d-none');
          validationAlert.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
          alert('Please select at least one seat before proceeding.');
        }
        return false;
      }
    });
  }

  // Toast notification helper
  function showToast(message, type = 'info') {
    const toastEl = document.getElementById('cinemaToast');
    const toastBody = document.getElementById('cinemaToastBody');
    if (toastEl && toastBody && window.bootstrap) {
      toastBody.textContent = message;
      const toast = new bootstrap.Toast(toastEl);
      toast.show();
    }
  }
});
