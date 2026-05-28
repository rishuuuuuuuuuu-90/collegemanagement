import React, { useEffect, useState, useCallback } from 'react';
import { listEvents } from '../api/events';
import { bookTicket } from '../api/tickets';
import { createPaymentIntent, verifyPayment } from '../api/payments';
import { useAuth } from '../context/AuthContext';
import EventCard from '../components/EventCard';
import './EventListing.css';

const DUMMY_PAYMENT_QR = `data:image/svg+xml;utf8,${encodeURIComponent(
  `<svg xmlns="http://www.w3.org/2000/svg" width="220" height="220" viewBox="0 0 220 220">
    <rect width="220" height="220" fill="#ffffff"/>
    <rect x="10" y="10" width="50" height="50" fill="#000000"/>
    <rect x="20" y="20" width="30" height="30" fill="#ffffff"/>
    <rect x="160" y="10" width="50" height="50" fill="#000000"/>
    <rect x="170" y="20" width="30" height="30" fill="#ffffff"/>
    <rect x="10" y="160" width="50" height="50" fill="#000000"/>
    <rect x="20" y="170" width="30" height="30" fill="#ffffff"/>
    <rect x="80" y="20" width="15" height="15" fill="#000000"/>
    <rect x="110" y="20" width="15" height="15" fill="#000000"/>
    <rect x="80" y="50" width="15" height="15" fill="#000000"/>
    <rect x="95" y="80" width="15" height="15" fill="#000000"/>
    <rect x="125" y="80" width="15" height="15" fill="#000000"/>
    <rect x="80" y="110" width="15" height="15" fill="#000000"/>
    <rect x="110" y="110" width="15" height="15" fill="#000000"/>
    <rect x="140" y="110" width="15" height="15" fill="#000000"/>
    <rect x="80" y="140" width="15" height="15" fill="#000000"/>
    <rect x="110" y="140" width="15" height="15" fill="#000000"/>
    <rect x="140" y="140" width="15" height="15" fill="#000000"/>
    <rect x="170" y="95" width="15" height="15" fill="#000000"/>
    <rect x="170" y="125" width="15" height="15" fill="#000000"/>
    <rect x="170" y="155" width="15" height="15" fill="#000000"/>
  </svg>`
)}`;

const EventsListing = () => {
  const { user } = useAuth();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState(null);
  const [bookingMsg, setBookingMsg] = useState('');
  const [bookingLoading, setBookingLoading] = useState(false);
  const [pendingPayment, setPendingPayment] = useState(null);

  const fetchEvents = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const params = { page, limit: 9, status: 'active' };
      if (search) params.search = search;
      if (category) params.category = category;
      const res = await listEvents(params);
      setEvents(res.data.data.events);
      setPagination(res.data.data.pagination);
    } catch (err) {
      setError('Failed to load events');
    } finally {
      setLoading(false);
    }
  }, [page, search, category]);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    fetchEvents();
  };

  const handleBook = async (event) => {
    if (!user) return;
    setBookingMsg('');
    if (event.price > 0) {
      setBookingLoading(true);
      try {
        const intentRes = await createPaymentIntent({ eventId: event._id });
        const { paymentIntentId, amount } = intentRes.data.data;
        setPendingPayment({ event, paymentIntentId, amount });
      } catch (err) {
        setBookingMsg(
          '❌ ' + (err?.response?.data?.message || 'Unable to start payment. Please try again.')
        );
      } finally {
        setBookingLoading(false);
      }
      return;
    }

    setBookingLoading(true);
    try {
      await bookTicket({ eventId: event._id });
      setBookingMsg(`🎟 Free ticket booked for "${event.title}"! Check My Tickets.`);
      fetchEvents();
    } catch (err) {
      setBookingMsg('❌ ' + (err?.response?.data?.message || 'Booking failed. Please try again.'));
    } finally {
      setBookingLoading(false);
    }
  };

  const handleConfirmPayment = async () => {
    if (!pendingPayment) return;
    setBookingLoading(true);
    setBookingMsg('');
    try {
      const { event, paymentIntentId } = pendingPayment;
      await bookTicket({ eventId: event._id, paymentIntentId });
      await verifyPayment({ paymentIntentId, eventId: event._id });
      setPendingPayment(null);
      setBookingMsg(`✅ Payment successful! Ticket booked for "${event.title}". Check My Tickets for your ticket QR code.`);
      fetchEvents();
    } catch (err) {
      setBookingMsg('❌ ' + (err?.response?.data?.message || 'Payment failed. Please try again.'));
    } finally {
      setBookingLoading(false);
    }
  };

  const categories = ['academic', 'cultural', 'sports', 'technical', 'social', 'other'];

  return (
    <div className="events-page">
      <div className="events-hero">
        <h1>Upcoming Events</h1>
        <p>Discover and book events at your college</p>
      </div>

      <div className="events-filters">
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            placeholder="Search events..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-input"
          />
          <button type="submit" className="btn-search">Search</button>
        </form>
        <div className="category-filters">
          <button
            className={`filter-btn ${category === '' ? 'active' : ''}`}
            onClick={() => { setCategory(''); setPage(1); }}
          >
            All
          </button>
          {categories.map((cat) => (
            <button
              key={cat}
              className={`filter-btn ${category === cat ? 'active' : ''}`}
              onClick={() => { setCategory(cat); setPage(1); }}
            >
              {cat.charAt(0).toUpperCase() + cat.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {bookingMsg && (
        <div className={`booking-alert ${bookingMsg.startsWith('❌') ? 'error' : 'success'}`}>
          {bookingMsg}
        </div>
      )}

      {pendingPayment && (
        <div className="payment-modal-overlay">
          <div className="payment-modal">
            <h3>Scan Dummy Payment QR</h3>
            <p className="payment-modal__event">{pendingPayment.event.title}</p>
            <img src={DUMMY_PAYMENT_QR} alt="Dummy payment QR" className="payment-modal__qr" />
            <p className="payment-modal__amount">Amount: ${Number(pendingPayment.amount).toFixed(2)}</p>
            <p className="payment-modal__hint">After scanning and paying, click "I Have Paid".</p>
            <div className="payment-modal__actions">
              <button
                className="payment-btn payment-btn--secondary"
                onClick={() => setPendingPayment(null)}
                disabled={bookingLoading}
              >
                Cancel
              </button>
              <button
                className="payment-btn payment-btn--primary"
                onClick={handleConfirmPayment}
                disabled={bookingLoading}
              >
                {bookingLoading ? 'Confirming...' : 'I Have Paid'}
              </button>
            </div>
          </div>
        </div>
      )}

      {loading && <div className="loading-spinner">Loading events...</div>}
      {error && <div className="error-msg">{error}</div>}

      {!loading && events.length === 0 && (
        <div className="no-events">No events found. Check back later!</div>
      )}

      <div className="events-grid">
        {events.map((event) => (
          <EventCard
            key={event._id}
            event={event}
            onBook={bookingLoading || pendingPayment ? null : handleBook}
          />
        ))}
      </div>

      {pagination && pagination.pages > 1 && (
        <div className="pagination">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="page-btn"
          >
            ← Prev
          </button>
          <span className="page-info">Page {page} of {pagination.pages}</span>
          <button
            onClick={() => setPage((p) => Math.min(pagination.pages, p + 1))}
            disabled={page === pagination.pages}
            className="page-btn"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
};

export default EventsListing;
