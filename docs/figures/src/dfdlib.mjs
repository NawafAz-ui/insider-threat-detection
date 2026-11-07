// Small SVG builder for Gane-Sarson data-flow diagrams (process = rounded box with an ID row,
// data store = open-ended box with an ID box, external entity = plain rectangle, flow = labelled arrow).
export const FONT = "Helvetica, Arial, sans-serif";
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

export class Diagram {
  constructor(w, h) { this.w = w; this.h = h; this.parts = []; }
  add(s) { this.parts.push(s); }

  text(x, y, lines, o = {}) {
    const size = o.size || 11, lh = o.lh || size * 1.22, anchor = o.anchor || "middle";
    const arr = Array.isArray(lines) ? lines : [lines];
    const y0 = o.valign === "middle" ? y - ((arr.length - 1) * lh) / 2 : y;
    const tsp = arr.map((t, i) => `<tspan x="${x}" y="${(y0 + i * lh).toFixed(1)}">${esc(t)}</tspan>`).join("");
    const halo = o.halo ? ` stroke="#fff" stroke-width="3.5" stroke-linejoin="round" paint-order="stroke"` : "";
    const tf = o.rotate ? ` transform="rotate(${o.rotate} ${x} ${y})"` : "";
    this.add(`<text font-family="${FONT}" font-size="${size}" text-anchor="${anchor}" fill="#000"${o.bold ? ' font-weight="700"' : ""}${o.italic ? ' font-style="italic"' : ""}${halo}${tf}>${tsp}</text>`);
  }

  entity(cx, cy, w, h, lines) {
    this.add(`<rect x="${cx - w / 2}" y="${cy - h / 2}" width="${w}" height="${h}" fill="#fff" stroke="#000" stroke-width="1.6"/>`);
    this.text(cx, cy + 4, lines, { size: 12.5, valign: "middle", lh: 15 });
    return { x1: cx - w / 2, y1: cy - h / 2, x2: cx + w / 2, y2: cy + h / 2 };
  }

  process(cx, cy, w, h, id, lines) {
    const x = cx - w / 2, y = cy - h / 2, idH = 19;
    this.add(`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="10" fill="#fff" stroke="#000" stroke-width="1.6"/>`);
    this.add(`<line x1="${x}" y1="${y + idH}" x2="${x + w}" y2="${y + idH}" stroke="#000" stroke-width="1.2"/>`);
    this.text(x + 9, y + 14, id, { size: 11.5, bold: true, anchor: "start" });
    this.text(cx, y + idH + (h - idH) / 2 + 4, lines, { size: 12.5, valign: "middle", lh: 15 });
    return { x1: x, y1: y, x2: x + w, y2: y + h };
  }

  // vertical data store: ID box on top, body open at the bottom, name written along the body
  storeVertical(cx, y1, y2, w, id, name) {
    const x1 = cx - w / 2, x2 = cx + w / 2, idH = 26;
    this.add(`<rect x="${x1}" y="${y1}" width="${w}" height="${idH}" fill="#fff" stroke="#000" stroke-width="1.6"/>`);
    this.add(`<path d="M${x1} ${y1 + idH} V${y2} M${x2} ${y1 + idH} V${y2}" fill="none" stroke="#000" stroke-width="1.6"/>`);
    this.text(cx, y1 + 18, id, { size: 12, bold: true });
    this.text(cx + 4.5, (y1 + idH + y2) / 2, name, { size: 12.5, rotate: -90 });
    return { x1, y1, x2, y2 };
  }

  // horizontal data store: ID box at the left end, body open at the right end, name written in the body
  storeHorizontal(x1, x2, cy, h, id, name) {
    const y1 = cy - h / 2, y2 = cy + h / 2, idW = 38;
    this.add(`<rect x="${x1}" y="${y1}" width="${idW}" height="${h}" fill="#fff" stroke="#000" stroke-width="1.6"/>`);
    this.add(`<path d="M${x1 + idW} ${y1} H${x2} M${x1 + idW} ${y2} H${x2}" fill="none" stroke="#000" stroke-width="1.6"/>`);
    this.text(x1 + idW / 2, cy + 4.5, id, { size: 12, bold: true });
    this.text((x1 + idW + x2) / 2, cy + 4.5, name, { size: 12.5 });
    return { x1, y1, x2, y2 };
  }

  arrow(points, o = {}) {
    const pts = points.map((p) => p.join(",")).join(" ");
    this.add(`<polyline points="${pts}" fill="none" stroke="#000" stroke-width="1.15" marker-end="url(#ah)"/>`);
    if (o.label) this.text(o.lx, o.ly, o.label, { size: 11, anchor: o.anchor || "middle", halo: true, lh: 12.4 });
  }

  svg() {
    return `<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="${this.w}" height="${this.h}" viewBox="0 0 ${this.w} ${this.h}">` +
      `<defs><marker id="open" viewBox="0 0 10 10" refX="9.5" refY="5" markerWidth="9" markerHeight="9" orient="auto"><path d="M1,1 L9.5,5 L1,9" fill="none" stroke="#000" stroke-width="1.4"/></marker><marker id="ah" viewBox="0 0 10 8" refX="9.5" refY="4" markerWidth="9" markerHeight="7.2" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="#000"/></marker></defs>` +
      `<rect width="${this.w}" height="${this.h}" fill="#fff"/>${this.parts.join("")}</svg>`;
  }
}

// ---- UML helpers (use-case and activity diagrams) ----
Diagram.prototype.actor = function (x, y, lines) {
  // stick figure centred at x, head top at y; label below
  this.add(`<circle cx="${x}" cy="${y + 9}" r="9" fill="#fff" stroke="#000" stroke-width="1.5"/>` +
    `<path d="M${x} ${y + 18} V${y + 46} M${x - 17} ${y + 28} H${x + 17} M${x} ${y + 46} L${x - 15} ${y + 66} M${x} ${y + 46} L${x + 15} ${y + 66}" fill="none" stroke="#000" stroke-width="1.5"/>`);
  this.text(x, y + 84, lines, { size: 12.5, lh: 15 });
};
Diagram.prototype.usecase = function (cx, cy, w, h, lines) {
  this.add(`<ellipse cx="${cx}" cy="${cy}" rx="${w / 2}" ry="${h / 2}" fill="#fff" stroke="#000" stroke-width="1.4"/>`);
  this.text(cx, cy + 4, lines, { size: 12.5, valign: "middle", lh: 15 });
  return { cx, cy, a: w / 2, b: h / 2 };
};
Diagram.prototype.boundary = function (x1, y1, x2, y2, title) {
  this.add(`<rect x="${x1}" y="${y1}" width="${x2 - x1}" height="${y2 - y1}" fill="none" stroke="#000" stroke-width="1.6"/>`);
  this.text((x1 + x2) / 2, y1 + 22, title, { size: 13.5, bold: true });
};
// point where the line from the centre of an ellipse towards (px, py) leaves the ellipse
export function ellipseEdge(e, px, py) {
  const dx = px - e.cx, dy = py - e.cy;
  const t = 1 / Math.sqrt((dx / e.a) ** 2 + (dy / e.b) ** 2);
  return [e.cx + dx * t, e.cy + dy * t];
}
Diagram.prototype.line = function (p, q) {
  this.add(`<line x1="${p[0].toFixed(1)}" y1="${p[1].toFixed(1)}" x2="${q[0].toFixed(1)}" y2="${q[1].toFixed(1)}" stroke="#000" stroke-width="1.2"/>`);
};
// dashed dependency arrow with an open arrowhead (UML include / extend)
Diagram.prototype.dashed = function (pts, o = {}) {
  const p = pts.map((q) => q.map((v) => v.toFixed(1)).join(",")).join(" ");
  this.add(`<polyline points="${p}" fill="none" stroke="#000" stroke-width="1.2" stroke-dasharray="6 4" marker-end="url(#open)"/>`);
  if (o.label) this.text(o.lx, o.ly, o.label, { size: 11.5, anchor: o.anchor || "middle", halo: true, italic: false });
};

// ---- UML activity-diagram helpers ----
Diagram.prototype.action = function (cx, cy, w, h, lines) {
  this.add(`<rect x="${cx - w / 2}" y="${cy - h / 2}" width="${w}" height="${h}" rx="14" fill="#fff" stroke="#000" stroke-width="1.5"/>`);
  this.text(cx, cy + 4.2, lines, { size: 12.5, valign: "middle", lh: 15 });
};
Diagram.prototype.objectNode = function (cx, cy, w, h, keyword, lines) {
  this.add(`<rect x="${cx - w / 2}" y="${cy - h / 2}" width="${w}" height="${h}" fill="#fff" stroke="#000" stroke-width="1.5"/>`);
  this.text(cx, cy - 2, keyword, { size: 11, italic: false });
  this.text(cx, cy + 13, lines, { size: 12.5 });
};
Diagram.prototype.initial = function (cx, cy) { this.add(`<circle cx="${cx}" cy="${cy}" r="8.5" fill="#000"/>`); };
Diagram.prototype.finalNode = function (cx, cy) {
  this.add(`<circle cx="${cx}" cy="${cy}" r="11" fill="#fff" stroke="#000" stroke-width="1.5"/><circle cx="${cx}" cy="${cy}" r="6.5" fill="#000"/>`);
};
Diagram.prototype.diamond = function (cx, cy, w, h) {
  this.add(`<polygon points="${cx},${cy - h / 2} ${cx + w / 2},${cy} ${cx},${cy + h / 2} ${cx - w / 2},${cy}" fill="#fff" stroke="#000" stroke-width="1.5"/>`);
};
Diagram.prototype.flow = function (pts, o = {}) {
  const p = pts.map((q) => q.join(",")).join(" ");
  this.add(`<polyline points="${p}" fill="none" stroke="#000" stroke-width="1.3" marker-end="url(#open)"/>`);
  if (o.label) this.text(o.lx, o.ly, o.label, { size: 11.5, anchor: o.anchor || "middle", halo: true });
};
