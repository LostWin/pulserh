import { useState, useMemo } from 'react';
import {
  ChevronLeft, ChevronRight, Download, Plus, Plane,
  Clock, FileText, BotMessageSquare, CalendarCheck,
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

// ─── Mock data ─────────────────────────────────────────────────────────────
const LEAVE_BALANCES = [
  {
    id: 'cp',
    icon: Plane,
    label: 'PAID LEAVE BALANCE',
    value: 22.5,
    unit: 'days',
    tag: '✓ Stable',
    tagColor: 'text-emerald-600 bg-emerald-50',
  },
  {
    id: 'rtt',
    icon: Clock,
    label: 'RTT BALANCE',
    value: 8.0,
    unit: 'days',
    tag: '⏰ Expires 31/12',
    tagColor: 'text-amber-600 bg-amber-50',
  },
  {
    id: 'sick',
    icon: FileText,
    label: 'SICK LEAVE (YTD)',
    value: 2,
    unit: 'days',
    tag: '+ New Entry',
    tagColor: 'text-red-500 bg-red-50',
  },
];

const ACTIVITY = [
  {
    id: 1,
    title: 'Paid Leave Validated',
    sub: 'By Sarah Connor · 2 hours ago',
    color: 'bg-emerald-500',
  },
  {
    id: 2,
    title: 'RTT Requested',
    sub: 'Pending approval · Yesterday',
    color: 'bg-amber-400',
  },
  {
    id: 3,
    title: 'Sick Leave Recorded',
    sub: 'Medical cert uploaded · 3 days ago',
    color: 'bg-red-400',
  },
];

// Calendar events keyed by "YYYY-MM-DD"
const CALENDAR_EVENTS = {
  '2023-11-03': { label: 'Validated\nLeave', color: '#1F524B', text: 'white' },
  '2023-11-16': { label: 'Pending\nRTT', color: '#DF4931', text: 'white' },
};

const WEEK_DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];

function getMonthMatrix(year, month) {
  // Returns a 6×7 matrix of day numbers (0 = empty)
  const firstDay = new Date(year, month, 1).getDay(); // 0=Sun
  const total = new Date(year, month + 1, 0).getDate();
  // Shift so Monday = 0
  const offset = (firstDay === 0 ? 6 : firstDay - 1);
  const cells = Array(offset).fill(0);
  for (let d = 1; d <= total; d++) cells.push(d);
  while (cells.length % 7 !== 0) cells.push(0);
  const weeks = [];
  for (let i = 0; i < cells.length; i += 7) weeks.push(cells.slice(i, i + 7));
  return weeks;
}

const MONTHS_FR = [
  'January','February','March','April','May','June',
  'July','August','September','October','November','December',
];

export default function Conges() {
  const { user } = useAuth();
  const today = new Date();
  const [current, setCurrent] = useState({ year: 2023, month: 10 }); // Nov 2023
  const [showModal, setShowModal] = useState(false);

  const weeks = useMemo(
    () => getMonthMatrix(current.year, current.month),
    [current.year, current.month],
  );

  const prev = () =>
    setCurrent(({ year, month }) =>
      month === 0 ? { year: year - 1, month: 11 } : { year, month: month - 1 },
    );

  const next = () =>
    setCurrent(({ year, month }) =>
      month === 11 ? { year: year + 1, month: 0 } : { year, month: month + 1 },
    );

  const goToday = () => setCurrent({ year: today.getFullYear(), month: today.getMonth() });

  const isToday = (d) =>
    d === today.getDate() &&
    current.month === today.getMonth() &&
    current.year === today.getFullYear();

  const eventKey = (d) => {
    if (!d) return null;
    const mm = String(current.month + 1).padStart(2, '0');
    const dd = String(d).padStart(2, '0');
    return `${current.year}-${mm}-${dd}`;
  };

  return (
    <div className="animate-fade-in-up space-y-6">

      {/* ── Page header ─────────────────────────────────────────── */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-brand-dark">Leave &amp; Calendar</h1>
          <p className="mt-0.5 text-sm text-brand-secondary/70">
            Review your current balance and upcoming absences.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            className="flex items-center gap-2 rounded-xl border border-brand-secondary/20 bg-white px-4 py-2.5 text-sm font-medium text-brand-dark shadow-sm hover:bg-brand-light transition-colors"
          >
            <Download size={15} />
            Export Statement
          </button>
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 rounded-xl bg-brand-danger px-4 py-2.5 text-sm font-bold text-white shadow-sm hover:opacity-90 transition-opacity"
          >
            <Plus size={15} />
            Request Leave
          </button>
        </div>
      </div>

      {/* ── Balance cards ────────────────────────────────────────── */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {LEAVE_BALANCES.map(({ id, icon: Icon, label, value, unit, tag, tagColor }) => (
          <div
            key={id}
            className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-5"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="grid h-9 w-9 place-items-center rounded-xl bg-brand-secondary/8">
                <Icon size={18} className="text-brand-secondary" />
              </div>
              <span className={`rounded-full px-2.5 py-0.5 text-[11px] font-semibold ${tagColor}`}>
                {tag}
              </span>
            </div>
            <p className="text-[10px] font-bold uppercase tracking-widest text-brand-secondary/50 mb-1">
              {label}
            </p>
            <p className="text-3xl font-extrabold text-brand-dark">
              {value}
              <span className="ml-1.5 text-base font-semibold text-brand-secondary/60">{unit}</span>
            </p>
          </div>
        ))}
      </div>

      {/* ── Calendar + Right panel ────────────────────────────────── */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">

        {/* Calendar */}
        <div className="lg:col-span-2 rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-5">
          {/* Month navigation */}
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-base font-bold text-brand-dark">
              {MONTHS_FR[current.month]} {current.year}
            </h2>
            <div className="flex items-center gap-1">
              <button
                onClick={prev}
                className="grid h-8 w-8 place-items-center rounded-lg border border-brand-secondary/15 text-brand-secondary hover:bg-brand-light transition-colors"
              >
                <ChevronLeft size={16} />
              </button>
              <button
                onClick={goToday}
                className="rounded-lg border border-brand-secondary/15 px-3 py-1.5 text-xs font-semibold text-brand-secondary hover:bg-brand-light transition-colors"
              >
                Today
              </button>
              <button
                onClick={next}
                className="grid h-8 w-8 place-items-center rounded-lg border border-brand-secondary/15 text-brand-secondary hover:bg-brand-light transition-colors"
              >
                <ChevronRight size={16} />
              </button>
            </div>
          </div>

          {/* Grid */}
          <div className="grid grid-cols-7 gap-px text-center">
            {WEEK_DAYS.map((d) => (
              <div
                key={d}
                className="pb-2 text-[10px] font-bold uppercase tracking-widest text-brand-secondary/50"
              >
                {d}
              </div>
            ))}
            {weeks.map((week, wi) =>
              week.map((day, di) => {
                const key = eventKey(day);
                const event = key ? CALENDAR_EVENTS[key] : null;
                const today_ = day && isToday(day);
                return (
                  <div
                    key={`${wi}-${di}`}
                    className={`relative min-h-[68px] rounded-xl p-1.5 text-xs transition-colors
                      ${day ? 'hover:bg-brand-light/60 cursor-pointer' : ''}
                      ${today_ ? 'ring-2 ring-brand-secondary' : ''}
                    `}
                  >
                    {day ? (
                      <>
                        <span
                          className={`flex h-6 w-6 items-center justify-center rounded-full font-semibold
                            ${today_ ? 'bg-brand-secondary text-white' : 'text-brand-dark'}
                          `}
                        >
                          {day}
                        </span>
                        {today_ && (
                          <span className="block text-[9px] text-brand-secondary/60 font-medium mt-0.5">
                            (Today)
                          </span>
                        )}
                        {event && (
                          <div
                            className="mt-1 rounded-lg px-1.5 py-1 text-[9px] font-bold leading-tight whitespace-pre-line"
                            style={{ backgroundColor: event.color, color: event.text }}
                          >
                            {event.label}
                          </div>
                        )}
                      </>
                    ) : null}
                  </div>
                );
              }),
            )}
          </div>
        </div>

        {/* Right panel */}
        <div className="space-y-5">

          {/* AI Suggestion */}
          <div className="rounded-2xl border border-purple-200 bg-gradient-to-br from-purple-50 to-purple-100/60 p-5 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <div className="grid h-8 w-8 place-items-center rounded-xl bg-purple-500/15">
                <BotMessageSquare size={16} className="text-purple-600" />
              </div>
              <span className="text-xs font-bold uppercase tracking-widest text-purple-600">
                Pulse AI Suggestion
              </span>
            </div>
            <p className="text-sm text-purple-900/80 leading-relaxed mb-4">
              You have <strong>22.5 days</strong> remaining. Would you like to schedule your winter
              holidays now to ensure project continuity?
            </p>
            <button className="w-full rounded-xl bg-brand-secondary py-2.5 text-sm font-bold text-white hover:bg-brand-dark transition-colors shadow-sm mb-2">
              Plan Dec 20–27
            </button>
            <button className="w-full rounded-xl border border-brand-secondary/20 py-2 text-sm font-medium text-brand-secondary hover:bg-white transition-colors">
              Remind me later
            </button>
          </div>

          {/* Recent Activity */}
          <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-5">
            <div className="flex items-center gap-2 mb-4">
              <div className="grid h-7 w-7 place-items-center rounded-lg bg-brand-secondary/10">
                <CalendarCheck size={14} className="text-brand-secondary" />
              </div>
              <h3 className="text-sm font-bold text-brand-dark">Recent Activity</h3>
            </div>
            <div className="space-y-3">
              {ACTIVITY.map((a) => (
                <div key={a.id} className="flex items-start gap-3">
                  <span className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${a.color}`} />
                  <div>
                    <p className="text-sm font-semibold text-brand-dark leading-snug">{a.title}</p>
                    <p className="text-[11px] text-brand-secondary/60">{a.sub}</p>
                  </div>
                </div>
              ))}
            </div>
            <button className="mt-4 w-full rounded-xl border border-brand-secondary/15 py-2 text-xs font-medium text-brand-secondary hover:bg-brand-light transition-colors">
              View History
            </button>
          </div>
        </div>
      </div>

      {/* ── Request Modal ─────────────────────────────────────────── */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-brand-dark mb-4">New Leave Request</h3>
            <div className="space-y-3">
              <div>
                <label className="block mb-1 text-xs font-semibold text-brand-secondary/60 uppercase tracking-widest">
                  Type
                </label>
                <select className="w-full rounded-xl border border-brand-secondary/20 px-3 py-2.5 text-sm text-brand-dark outline-none focus:border-brand-secondary">
                  <option>Paid Leave</option>
                  <option>RTT</option>
                  <option>Sick Leave</option>
                  <option>Unpaid</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block mb-1 text-xs font-semibold text-brand-secondary/60 uppercase tracking-widest">From</label>
                  <input type="date" className="w-full rounded-xl border border-brand-secondary/20 px-3 py-2.5 text-sm text-brand-dark outline-none focus:border-brand-secondary" />
                </div>
                <div>
                  <label className="block mb-1 text-xs font-semibold text-brand-secondary/60 uppercase tracking-widest">To</label>
                  <input type="date" className="w-full rounded-xl border border-brand-secondary/20 px-3 py-2.5 text-sm text-brand-dark outline-none focus:border-brand-secondary" />
                </div>
              </div>
              <div>
                <label className="block mb-1 text-xs font-semibold text-brand-secondary/60 uppercase tracking-widest">Note (optional)</label>
                <textarea
                  rows={3}
                  className="w-full rounded-xl border border-brand-secondary/20 px-3 py-2.5 text-sm text-brand-dark outline-none focus:border-brand-secondary resize-none"
                  placeholder="Add a note for your manager…"
                />
              </div>
            </div>
            <div className="flex gap-3 mt-5">
              <button
                onClick={() => setShowModal(false)}
                className="flex-1 rounded-xl border border-brand-secondary/20 py-2.5 text-sm font-medium text-brand-secondary hover:bg-brand-light transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => setShowModal(false)}
                className="flex-1 rounded-xl bg-brand-secondary py-2.5 text-sm font-bold text-white hover:bg-brand-dark transition-colors"
              >
                Submit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
