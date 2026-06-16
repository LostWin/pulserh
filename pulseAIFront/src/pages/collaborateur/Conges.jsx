import { useEffect, useMemo, useState } from 'react';
import {
  ChevronLeft, ChevronRight, Download, Plus,
  BotMessageSquare, CalendarCheck,
} from 'lucide-react';

import { api } from '../../lib/api';

const WEEK_DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];
const MONTHS_FR = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

function getMonthMatrix(year, month) {
  const firstDay = new Date(year, month, 1).getDay();
  const total = new Date(year, month + 1, 0).getDate();
  const offset = firstDay === 0 ? 6 : firstDay - 1;
  const cells = Array(offset).fill(0);
  for (let day = 1; day <= total; day += 1) cells.push(day);
  while (cells.length % 7 !== 0) cells.push(0);
  const weeks = [];
  for (let index = 0; index < cells.length; index += 7) weeks.push(cells.slice(index, index + 7));
  return weeks;
}

export default function Conges() {
  const today = new Date();
  const [overview, setOverview] = useState(null);
  const [current, setCurrent] = useState({ year: today.getFullYear(), month: today.getMonth() });
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ leave_type: 'Congés Payés', start_date: '', end_date: '', reason: '' });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const loadOverview = async () => {
    try {
      const data = await api.get('/leaves/me');
      setOverview(data);
    } catch (err) {
      setError(err.message || 'Impossible de charger les congés.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOverview();
  }, []);

  const weeks = useMemo(() => getMonthMatrix(current.year, current.month), [current]);

  const eventMap = useMemo(() => {
    const map = {};
    (overview?.calendar_events || []).forEach((event) => {
      map[event.date] = event;
    });
    return map;
  }, [overview]);

  const prev = () => setCurrent(({ year, month }) => (month === 0 ? { year: year - 1, month: 11 } : { year, month: month - 1 }));
  const next = () => setCurrent(({ year, month }) => (month === 11 ? { year: year + 1, month: 0 } : { year, month: month + 1 }));
  const goToday = () => setCurrent({ year: today.getFullYear(), month: today.getMonth() });

  const isToday = (day) => day === today.getDate() && current.month === today.getMonth() && current.year === today.getFullYear();
  const eventKey = (day) => {
    if (!day) return null;
    return `${current.year}-${String(current.month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
  };

  const submitRequest = async () => {
    if (!form.start_date || !form.end_date) return;
    setSubmitting(true);
    setError('');
    try {
      await api.post('/leaves/requests', form);
      setShowModal(false);
      setForm({ leave_type: 'Congés Payés', start_date: '', end_date: '', reason: '' });
      await loadOverview();
    } catch (err) {
      setError(err.message || 'Impossible de soumettre la demande.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="animate-fade-in-up space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-brand-dark">Leave &amp; Calendar</h1>
          <p className="mt-0.5 text-sm text-brand-secondary/70">Review your real balance and upcoming absences.</p>
          {error ? <p className="mt-2 text-sm text-brand-warning">{error}</p> : null}
        </div>
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-2 rounded-xl border border-brand-secondary/20 bg-white px-4 py-2.5 text-sm font-medium text-brand-dark shadow-sm hover:bg-brand-light transition-colors">
            <Download size={15} />
            Export Statement
          </button>
          <button onClick={() => setShowModal(true)} className="flex items-center gap-2 rounded-xl bg-brand-danger px-4 py-2.5 text-sm font-bold text-white shadow-sm hover:opacity-90 transition-opacity">
            <Plus size={15} />
            Request Leave
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {(overview?.balances || []).map((item) => {
          const Icon = item.id === 'cp' ? Plus : item.id === 'rtt' ? CalendarCheck : Download;
          return (
            <div key={item.id} className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="grid h-9 w-9 place-items-center rounded-xl bg-brand-secondary/8">
                  <Icon size={18} className="text-brand-secondary" />
                </div>
                <span className={`rounded-full px-2.5 py-0.5 text-[11px] font-semibold ${item.tag_color}`}>{item.tag}</span>
              </div>
              <p className="text-[10px] font-bold uppercase tracking-widest text-brand-secondary/50 mb-1">{item.label}</p>
              <p className="text-3xl font-extrabold text-brand-dark">{item.value}<span className="ml-1.5 text-base font-semibold text-brand-secondary/60">{item.unit}</span></p>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-5">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-base font-bold text-brand-dark">{MONTHS_FR[current.month]} {current.year}</h2>
            <div className="flex items-center gap-1">
              <button onClick={prev} className="grid h-8 w-8 place-items-center rounded-lg border border-brand-secondary/15 text-brand-secondary hover:bg-brand-light transition-colors"><ChevronLeft size={16} /></button>
              <button onClick={goToday} className="rounded-lg border border-brand-secondary/15 px-3 py-1.5 text-xs font-semibold text-brand-secondary hover:bg-brand-light transition-colors">Today</button>
              <button onClick={next} className="grid h-8 w-8 place-items-center rounded-lg border border-brand-secondary/15 text-brand-secondary hover:bg-brand-light transition-colors"><ChevronRight size={16} /></button>
            </div>
          </div>

          <div className="grid grid-cols-7 gap-px text-center">
            {WEEK_DAYS.map((day) => (
              <div key={day} className="pb-2 text-[10px] font-bold uppercase tracking-widest text-brand-secondary/50">{day}</div>
            ))}
            {weeks.map((week, weekIndex) => week.map((day, dayIndex) => {
              const key = eventKey(day);
              const event = key ? eventMap[key] : null;
              const todayCell = day && isToday(day);
              return (
                <div key={`${weekIndex}-${dayIndex}`} className={`relative min-h-[68px] rounded-xl p-1.5 text-xs ${day ? 'hover:bg-brand-light/60' : ''} ${todayCell ? 'ring-2 ring-brand-secondary' : ''}`}>
                  {day ? (
                    <>
                      <span className={`flex h-6 w-6 items-center justify-center rounded-full font-semibold ${todayCell ? 'bg-brand-secondary text-white' : 'text-brand-dark'}`}>{day}</span>
                      {event ? (
                        <div className="mt-1 rounded-lg px-1.5 py-1 text-[9px] font-bold leading-tight whitespace-pre-line" style={{ backgroundColor: event.color, color: event.text }}>
                          {event.label}
                        </div>
                      ) : null}
                    </>
                  ) : null}
                </div>
              );
            }))}
          </div>
        </div>

        <div className="space-y-5">
          <div className="rounded-2xl border border-purple-200 bg-gradient-to-br from-purple-50 to-purple-100/60 p-5 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <div className="grid h-8 w-8 place-items-center rounded-xl bg-purple-500/15">
                <BotMessageSquare size={16} className="text-purple-600" />
              </div>
              <span className="text-xs font-bold uppercase tracking-widest text-purple-600">Pulse AI Suggestion</span>
            </div>
            <p className="text-sm text-purple-900/80 leading-relaxed mb-4">{overview?.ai_suggestion?.message || 'Chargement de la suggestion…'}</p>
            <button className="w-full rounded-xl bg-brand-secondary py-2.5 text-sm font-bold text-white hover:bg-brand-dark transition-colors shadow-sm mb-2">
              {overview?.ai_suggestion?.primary_action || 'Planifier'}
            </button>
            <button className="w-full rounded-xl border border-brand-secondary/20 py-2 text-sm font-medium text-brand-secondary hover:bg-white transition-colors">
              {overview?.ai_suggestion?.secondary_action || 'Plus tard'}
            </button>
          </div>

          <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-5">
            <div className="flex items-center gap-2 mb-4">
              <div className="grid h-7 w-7 place-items-center rounded-lg bg-brand-secondary/10">
                <CalendarCheck size={14} className="text-brand-secondary" />
              </div>
              <h3 className="text-sm font-bold text-brand-dark">Recent Activity</h3>
            </div>
            <div className="space-y-3">
              {(overview?.activity || []).map((item) => (
                <div key={item.id} className="flex items-start gap-3">
                  <span className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${item.color}`} />
                  <div>
                    <p className="text-sm font-semibold text-brand-dark leading-snug">{item.title}</p>
                    <p className="text-[11px] text-brand-secondary/60">{item.sub}</p>
                  </div>
                </div>
              ))}
              {loading ? <p className="text-sm text-brand-secondary/60">Chargement…</p> : null}
            </div>
          </div>
        </div>
      </div>

      {showModal ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-brand-dark mb-4">New Leave Request</h3>
            <div className="space-y-3">
              <div>
                <label className="block mb-1 text-xs font-semibold text-brand-secondary/60 uppercase tracking-widest">Type</label>
                <select value={form.leave_type} onChange={(event) => setForm((prev) => ({ ...prev, leave_type: event.target.value }))} className="w-full rounded-xl border border-brand-secondary/20 px-3 py-2.5 text-sm text-brand-dark outline-none focus:border-brand-secondary">
                  <option>Congés Payés</option>
                  <option>RTT</option>
                  <option>Maladie</option>
                  <option>Autres</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block mb-1 text-xs font-semibold text-brand-secondary/60 uppercase tracking-widest">From</label>
                  <input type="date" value={form.start_date} onChange={(event) => setForm((prev) => ({ ...prev, start_date: event.target.value }))} className="w-full rounded-xl border border-brand-secondary/20 px-3 py-2.5 text-sm text-brand-dark outline-none focus:border-brand-secondary" />
                </div>
                <div>
                  <label className="block mb-1 text-xs font-semibold text-brand-secondary/60 uppercase tracking-widest">To</label>
                  <input type="date" value={form.end_date} onChange={(event) => setForm((prev) => ({ ...prev, end_date: event.target.value }))} className="w-full rounded-xl border border-brand-secondary/20 px-3 py-2.5 text-sm text-brand-dark outline-none focus:border-brand-secondary" />
                </div>
              </div>
              <div>
                <label className="block mb-1 text-xs font-semibold text-brand-secondary/60 uppercase tracking-widest">Note (optional)</label>
                <textarea rows={3} value={form.reason} onChange={(event) => setForm((prev) => ({ ...prev, reason: event.target.value }))} className="w-full rounded-xl border border-brand-secondary/20 px-3 py-2.5 text-sm text-brand-dark outline-none focus:border-brand-secondary resize-none" placeholder="Add a note for your manager…" />
              </div>
            </div>
            <div className="flex gap-3 mt-5">
              <button onClick={() => setShowModal(false)} className="flex-1 rounded-xl border border-brand-secondary/20 py-2.5 text-sm font-medium text-brand-secondary hover:bg-brand-light transition-colors">Cancel</button>
              <button onClick={submitRequest} disabled={submitting} className="flex-1 rounded-xl bg-brand-secondary py-2.5 text-sm font-bold text-white hover:bg-brand-dark transition-colors disabled:opacity-60">
                {submitting ? 'Submit…' : 'Submit'}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
