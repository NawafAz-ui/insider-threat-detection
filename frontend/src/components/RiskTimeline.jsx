import { riskClass } from "../format.js";

const COLORS = { hi: "#c0392b", mid: "#b45f06", edge: "#5b7186" };
const W = 760, H = 230, L = 44, R = 16, T = 16, B = 34;
const PW = W - L - R, PH = H - T - B;
const day = (iso) => new Date(iso).toLocaleDateString(undefined, { dateStyle: "medium" });

// One dot per session: height is the risk score, flagged sessions are larger and coloured. Click a dot to open it.
export default function RiskTimeline({ sessions, threshold }) {
  if (!sessions.length) return null;
  const times = sessions.map((s) => +new Date(s.start));
  const t0 = Math.min(...times), t1 = Math.max(...times);
  const x = (t) => L + (t1 === t0 ? PW / 2 : ((t - t0) / (t1 - t0)) * PW);
  const y = (r) => T + PH - (Math.min(Math.max(r, 0), 100) / 100) * PH;
  const flagged = sessions.filter((s) => s.flagged).length;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" role="group"
      aria-label={`Risk score of ${sessions.length} sessions over time, ${flagged} flagged. Each dot opens that session.`}>
      {[0, 50, 100].map((v) => (
        <g key={v}>
          <line x1={L} x2={W - R} y1={y(v)} y2={y(v)} stroke="#dfe4ea" />
          <text x={L - 8} y={y(v)} textAnchor="end" dominantBaseline="central" fontSize="12" fill="#5b6877">{v}</text>
        </g>
      ))}
      {threshold > 0 && (
        <g>
          <line x1={L} x2={W - R} y1={y(threshold)} y2={y(threshold)} stroke="#0e7c86" strokeDasharray="5 4" />
          <text x={W - R} y={y(threshold) - 6} textAnchor="end" fontSize="12" fill="#0a5c64">flag threshold {threshold}</text>
        </g>
      )}
      {sessions.map((s) => (
        <a key={s.session_id} href={`#/session/${s.session_id}`} aria-label={`${day(s.start)}, risk ${s.risk_score.toFixed(0)}${s.flagged ? ", flagged" : ""}`}>
          <circle cx={x(+new Date(s.start))} cy={y(s.risk_score)} r={s.flagged ? 6 : 3}
            fill={s.flagged ? COLORS[riskClass(s.risk_score)] : "#9aa5b1"} opacity={s.flagged ? 1 : 0.8}>
            <title>{`${day(s.start)}: risk ${s.risk_score.toFixed(0)}${s.flagged ? " (flagged)" : ""}`}</title>
          </circle>
        </a>
      ))}
      <text x={L} y={H - 8} fontSize="12" fill="#5b6877">{day(sessions[0].start)}</text>
      <text x={W - R} y={H - 8} textAnchor="end" fontSize="12" fill="#5b6877">{day(sessions[sessions.length - 1].start)}</text>
    </svg>
  );
}
