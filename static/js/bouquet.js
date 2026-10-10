/* Footer bouquet: the Desmos graph 4ovfzmudxu redrawn on a canvas. Inequalities are evaluated per pixel
   the way Desmos does it, curves are drawn as paths, and every flower is its own group so it can sway,
   bloom under the pointer and shed petals when clicked. Clicking the wrapping opens the note. */
(function () {
    const canvas = document.getElementById('bouquet-canvas');
    if (!canvas) return;
    const root = canvas.closest('.bouquet');
    const note = document.getElementById('bouquet-note');
    const ctx = canvas.getContext('2d');
    const { sin, cos, sqrt, atan2, abs, exp, pow, PI } = Math;
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Desmos palette c1..c15 (c11 is clamped to white)
    const C = [null, '#FFB6C1', '#DB92B2', '#CEE586', '#F5EDAF', '#DBED51', '#60ACCC', '#432BD9', '#9FDCF2',
        '#EBD898', '#E36495', '#FFFFFF', '#E1A148', '#DAE7F7', '#DABFE8', '#6F8BC8'];

    // The petal-ish curve the wrapping is built from
    const r = t => exp(sin(t)) - cos(4 * t) + pow(sin(t / -2.4), 5);
    const superellipse = (x, y, cx1, cy1, cx2, cy2, a, b, c, d, p, lim) =>
        pow(abs((x - cx1) / a + (y - cy1) / b), p) + pow(abs(-(x - cx2) / c + (y - cy2) / d), p) <= lim;
    const ellipse = (x, y, angle, x1, y1, x2, y2, ra, rb, lim) => {
        const cs = cos(angle), sn = sin(angle);
        const u = (x - x1) * cs + (y - y1) * sn;
        const v = -(x - x2) * sn + (y - y2) * cs;
        return u * u / (ra * ra) + v * v / (rb * rb) <= lim;
    };
    const fourPetal = (x, y, cx, cy, angle) => {
        const cs = cos(angle), sn = sin(angle);
        const u = (x - cx) * cs + (y - cy) * sn;
        const v = -(x - cx) * sn + (y - cy) * cs;
        return sqrt(u * u + v * v) <= 1.2 + cos(4 * atan2(v, u));
    };

    // In Desmos draw order. f: inequality, path: curve. fill/line/lineOp default to Desmos' 0.4 / 2.5 / 0.9.
    const LAYERS = [
        { g: 'base', c: C[5], line: 4, path: { t: [0, 2 * PI], xy: t => [3.2 + 4 * cos(t), -3 + 15 * sin(t)], keep: (x, y) => x < 0.8 && y < 7 } },
        { g: 'leafR', c: C[5], fill: 1, line: 0, f: (x, y) => sqrt((x - 7) ** 2 + (y + 6) ** 2) <= 5 * cos(9 * atan2(y + 9, x - 2)) },
        { g: 'leafL', c: C[3], fill: 1, line: 0, f: (x, y) => sqrt((x + 6) ** 2 + (y + 6) ** 2) <= 6 * cos(6 * atan2(y + 9, x + 1)) },
        { g: 'buds', c: C[1], fill: 0.4, line: 0, f: (x, y) => ellipse(x, y, -0.7, -5, 1, -5, 0.6, 3, 1.2, 1.3) },
        { g: 'buds', c: C[1], line: 0, f: (x, y) => ellipse(x, y, 1.45837, -4, 2.3, -4, -6, 3.3, 1.4, 1.3) },
        { g: 'sun', c: C[12], fill: 0.8, line: 0, f: (x, y) => superellipse(x, y, -8, 6, -8, 7, cos(-1), sin(-0.4), sin(-0.4), cos(-0.4), 0.5, 5) },
        { g: 'sun', c: C[4], fill: 1, line: 0, f: (x, y) => superellipse(x, y, -8, 6, -8, 7, cos(-1), sin(-0.4), sin(-0.4), cos(-0.4), 0.5, 4.5) },
        { g: 'sun', c: C[9], fill: 1, lineOp: 0, f: (x, y) => superellipse(x, y, -8, 6, -8, 7, cos(-1), sin(-0.4), sin(-0.4), cos(-0.4), 0.5, 4) },
        { g: 'sun', c: C[10], fill: 1, line: 0, f: (x, y) => superellipse(x, y, -10, 6, -8, 7, 1, sin(-0.4), sin(-0.4), cos(-0.4), 0.5, 3.5) },
        { g: 'sun', c: C[4], fill: 1, f: (x, y) => superellipse(x, y, -10, 6, -8, 7, 1, sin(-0.4), sin(-0.4), cos(-0.4), 0.5, 3) },
        { g: 'sun', c: C[11], fill: 1, line: 0, f: (x, y) => superellipse(x, y, -10, 6, -8, 7, 1, sin(-0.4), sin(-0.4), cos(-0.4), 0.3, 2) },
        { g: 'base', c: C[5], line: 4, path: { t: [-0.7, 3], xy: x => [x, -((x - 3.2) ** 2) + 0.5] } },
        { g: 'base', c: C[3], line: 5, path: { t: [-3.3, 0.8], xy: x => [x, 8 - ((0.4587 * x + 4.53) ** 2) + 0.5] } },
        { g: 'base', c: C[12], fill: 0.4, path: { t: [0, 24], xy: t => [1.8 * r(t) * cos(t), 1.8 * (r(t) * sin(t) - 6)] } },
        { g: 'base', c: C[4], fill: 0.9, line: 3, path: { t: [0, 24 * PI], xy: t => [r(t) * cos(t), r(t) * sin(t) - 11] } },
        { g: 'base', c: C[9], line: 1, path: { t: [0, 12 * PI], xy: t => [r(t) * cos(t), r(t) * sin(t) - 11] } },
        { g: 'base', c: '#2D70B3', line: 1, path: { t: [0, 2 * PI], xy: t => [1.7 * r(t) * cos(t), 1.7 * (r(t) * sin(t) - 6.6)] } },
        { g: 'violet', c: '#6042A6', fill: 1, line: 0, f: (x, y) => sqrt(x * x + (y - 5) ** 2) <= 4 * cos(15 * atan2(y - 7.3, x - 0.3)) },
        { g: 'violet', c: C[14], fill: 1, f: (x, y) => sqrt(x * x + (y - 5) ** 2) <= 3 * cos(15 * atan2(y - 7.3, x - 0.3)) },
        { g: 'violet', c: C[14], f: (x, y) => sqrt(x * x + (y - 5) ** 2) <= 3 * cos(24 * atan2(y - 7.3, x - 0.3)) },
        { g: 'violet', c: C[13], fill: 0.8, f: (x, y) => sqrt(x * x + (y - 6.34) ** 2) <= 2 * cos(8 * atan2(y - 7.3, x - 0.3)) },
        { g: 'sky', c: C[6], fill: 0.7, line: 0, f: (x, y) => sqrt((x - 4.1) ** 2 + (y - 2) ** 2) <= 5 * cos(6 * atan2(y - 3, x - 4)) },
        { g: 'sky', c: C[8], fill: 1, lineOp: 0, f: (x, y) => sqrt((x - 4.1) ** 2 + (y - 2) ** 2) <= 4 * cos(7 * atan2(y - 3, x - 4)) },
        { g: 'sky', c: C[13], fill: 1, lineOp: 1, f: (x, y) => sqrt((x - 4.1) ** 2 + (y - 2) ** 2) <= 2 * cos(5 * atan2(y - 3, x - 4.1)) },
        { g: 'buds', c: C[2], fill: 1, line: 0, f: (x, y) => ellipse(x, y, 2.1, -4, 2, 0, -5, 3.3, 1.4, 1) },
        { g: 'buds', c: C[10], fill: 1, line: 0, f: (x, y) => ellipse(x, y, 1.45837, -4, 1.8, -4, -6, 3.3, 1.4, 1) },
        { g: 'buds', c: C[1], fill: 1, line: 1, f: (x, y) => ellipse(x, y, -0.7, -5, 0.6, -5, 0.6, 3, 1.2, 1) },
        { g: 'bell', c: C[8], fill: 1, line: 0, f: (x, y) => superellipse(x, y, 8, -12, 8, -10, cos(0.2), sin(0.3), sin(0.2), cos(0.4), 0.5, 3) },
        { g: 'bell', c: C[11], fill: 0.8, line: 0, f: (x, y) => superellipse(x, y, 8, -12, 8, -10.5, cos(0.3), sin(0.4), sin(0.2), cos(0.4), 0.5, 2) },
        { g: 'starL', c: C[15], f: (x, y) => fourPetal(x, y, -10, -10, 1.2) },
        { g: 'starR', c: C[13], fill: 0.9, f: (x, y) => fourPetal(x, y, 6, -3.94, 0.4) },
    ];

    // Each flower turns and blooms around its own pivot; `box` bounds its pixels (world units, x0 y0 x1 y1)
    const GROUPS = {
        base: { pivot: [0, -15] },
        leafR: { pivot: [3, -7], box: [1.8, -10, 11.5, -1.6] },
        leafL: { pivot: [-1, -6], box: [-11.7, -10.6, 0.2, 0.4] },
        buds: { pivot: [-4.5, 1.5], box: [-8.4, -2.1, -1, 6.4] },
        sun: { pivot: [-8, 6.2], box: [-15.5, -1.5, 0, 14] },
        violet: { pivot: [0, 5], box: [-4.4, 0.6, 4.4, 9.4] },
        sky: { pivot: [4.1, 2], box: [-1.3, -2.6, 9.5, 7.1] },
        bell: { pivot: [8, -11.8], box: [5.6, -14.6, 9.6, -9.1] },
        starL: { pivot: [-10, -10], box: [-12.5, -12.5, -7.5, -7.5] },
        starR: { pivot: [6, -3.94], box: [3.5, -6.4, 8.5, -1.5] },
    };
    const VIEW = { x0: -19.5, x1: 14, y0: -19, y1: 17 };   // room for a flower to bloom without clipping
    const DESMOS_PX_PER_UNIT = 8;   // the graph was drawn at roughly this zoom; line widths scale from it
    const SS = 2;                    // supersamples per pixel side, for smooth edges
    const HEADROOM = 1.2;            // raster a little sharper than needed so a blooming flower stays crisp

    Object.keys(GROUPS).forEach((name, i) => Object.assign(GROUPS[name], {
        name, angle: 0, spin: 0, scale: 1, phase: i * 1.7,
        colors: [...new Set(LAYERS.filter(L => L.g === name).map(L => L.c))],
    }));

    let k = 0, dpr = 1;              // CSS px per world unit, device pixel ratio
    let ready = false, started = false, frame = 0, last = 0;
    let pointer = null, hovered = null, lean = 0;
    const petals = [];
    const toX = x => (x - VIEW.x0) * k;
    const toY = y => (VIEW.y1 - y) * k;

    function hexRgb(hex) {
        const n = parseInt(hex.slice(1), 16);
        return [n >> 16, (n >> 8) & 255, n & 255];
    }

    // Tight box for one inequality inside its group's box, from a coarse scan
    function tightBox(L, box) {
        const b = [Infinity, Infinity, -Infinity, -Infinity];
        for (let x = box[0]; x <= box[2]; x += 0.1)
            for (let y = box[1]; y <= box[3]; y += 0.1)
                if (L.f(x, y)) { b[0] = Math.min(b[0], x); b[1] = Math.min(b[1], y); b[2] = Math.max(b[2], x); b[3] = Math.max(b[3], y); }
        if (b[0] === Infinity) return null;
        return [Math.max(box[0], b[0] - 0.4), Math.max(box[1], b[1] - 0.4), Math.min(box[2], b[2] + 0.4), Math.min(box[3], b[3] + 0.4)];
    }

    // Paint an inequality like Desmos does: fill the region, then stroke its boundary
    function rasterize(L) {
        const box = L.box || (L.box = tightBox(L, GROUPS[L.g].box));
        if (!box) return;
        const R = k * dpr * HEADROOM;                    // device px per unit
        const w = Math.ceil((box[2] - box[0]) * R), h = Math.ceil((box[3] - box[1]) * R);
        const sw = w * SS, sh = h * SS, step = 1 / (R * SS);
        const inside = new Uint8Array(sw * sh);
        for (let j = 0; j < sh; j++) {
            const y = box[3] - (j + 0.5) * step;
            for (let i = 0; i < sw; i++) inside[j * sw + i] = L.f(box[0] + (i + 0.5) * step, y) ? 1 : 0;
        }

        const fillOp = L.fill ?? 0.4, lineOp = L.lineOp ?? 0.9;
        const half = (L.line ?? 2.5) * (k / DESMOS_PX_PER_UNIT) * dpr * HEADROOM * SS / 2;   // in subsamples
        let stroke = null;
        if (lineOp > 0 && half > 0) {
            stroke = new Uint8Array(sw * sh);
            const rad = Math.ceil(half), r2 = half * half;
            for (let j = 0; j < sh; j++) for (let i = 0; i < sw; i++) {
                const v = inside[j * sw + i];
                if ((i + 1 < sw && inside[j * sw + i + 1] !== v) || (j + 1 < sh && inside[(j + 1) * sw + i] !== v)) {
                    for (let dy = -rad; dy <= rad; dy++) for (let dx = -rad; dx <= rad; dx++) {
                        const ii = i + dx, jj = j + dy;
                        if (dx * dx + dy * dy <= r2 && ii >= 0 && jj >= 0 && ii < sw && jj < sh) stroke[jj * sw + ii] = 1;
                    }
                }
            }
        }

        const image = new ImageData(w, h), px = image.data, [cr, cg, cb] = hexRgb(L.c);
        for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
            let fill = 0, line = 0;
            for (let sy = 0; sy < SS; sy++) for (let sx = 0; sx < SS; sx++) {
                const s = (y * SS + sy) * sw + x * SS + sx;
                fill += inside[s];
                if (stroke) line += stroke[s];
            }
            fill /= SS * SS; line = (line / (SS * SS)) * lineOp;
            const o = (y * w + x) * 4;
            px[o] = cr; px[o + 1] = cg; px[o + 2] = cb;
            px[o + 3] = 255 * (line + fill * fillOp * (1 - line));
        }
        const bitmap = document.createElement('canvas');
        bitmap.width = w; bitmap.height = h;
        bitmap.getContext('2d').putImageData(image, 0, 0);
        L.bitmap = bitmap;
        L.alpha = { data: px, w, h, R };                 // kept for hit testing
    }

    function tracePath(L) {
        const { t: [t0, t1], xy, keep } = L.path;
        const steps = Math.ceil((t1 - t0) * 60);
        const path = new Path2D();
        let pen = false;
        for (let s = 0; s <= steps; s++) {
            const [x, y] = xy(t0 + (t1 - t0) * s / steps);
            if (keep && !keep(x, y)) { pen = false; continue; }
            pen ? path.lineTo(toX(x), toY(y)) : path.moveTo(toX(x), toY(y));
            pen = true;
        }
        L.shape = path;
    }

    function size() {
        const width = canvas.clientWidth;
        if (!width) return false;
        k = width / (VIEW.x1 - VIEW.x0);
        dpr = Math.min(window.devicePixelRatio || 1, 2);
        canvas.width = Math.round(width * dpr);
        canvas.height = Math.round((VIEW.y1 - VIEW.y0) * k * dpr);
        return true;
    }

    // Build every layer, yielding to the browser between them; with `animate` each one grows in as it lands
    async function build(animate) {
        if (!size()) return;
        ready = false;
        for (const L of LAYERS) {
            L.path ? tracePath(L) : rasterize(L);
            L.born = animate ? performance.now() : -Infinity;
            if (animate) { draw(L.born); await new Promise(done => setTimeout(done, 60)); }
        }
        ready = true;
        draw(performance.now());
    }

    function transform(target, G) {
        const [px, py] = G.pivot;
        const [bx, by] = GROUPS.base.pivot;
        target.setTransform(dpr, 0, 0, dpr, 0, 0);
        target.translate(toX(bx), toY(by));              // the whole bouquet leans from the bottom of the wrap
        target.rotate(lean);
        target.translate(-toX(bx), -toY(by));
        if (G.name === 'base') return;
        target.translate(toX(px), toY(py));
        target.rotate(-G.angle);
        target.scale(G.scale, G.scale);
        target.translate(-toX(px), -toY(py));
    }

    function draw(now) {
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        for (const L of LAYERS) {
            if (L.born === undefined || (!L.bitmap && !L.shape)) continue;
            const G = GROUPS[L.g];
            const age = Math.min(1, (now - L.born) / 450);
            const ease = 1 - (1 - age) ** 3;
            transform(ctx, G);
            if (ease < 1) {                               // grow in from the flower's centre
                const [px, py] = G.pivot;
                ctx.translate(toX(px), toY(py));
                ctx.scale(0.6 + 0.4 * ease, 0.6 + 0.4 * ease);
                ctx.translate(-toX(px), -toY(py));
            }
            if (L.bitmap) {
                const b = L.box;
                ctx.globalAlpha = ease;
                ctx.drawImage(L.bitmap, toX(b[0]), toY(b[3]), (b[2] - b[0]) * k, (b[3] - b[1]) * k);
            } else {
                if (L.fill !== undefined) { ctx.fillStyle = L.c; ctx.globalAlpha = ease * L.fill; ctx.fill(L.shape); }
                ctx.strokeStyle = L.c;
                ctx.globalAlpha = ease * (L.lineOp ?? 0.9);
                ctx.lineWidth = (L.line ?? 2.5) * k / DESMOS_PX_PER_UNIT;
                ctx.lineJoin = ctx.lineCap = 'round';
                ctx.stroke(L.shape);
            }
        }
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        for (const p of petals) {
            ctx.globalAlpha = Math.max(0, 1 - p.age / p.life);
            ctx.fillStyle = p.c;
            ctx.save();
            ctx.translate(toX(p.x), toY(p.y));
            ctx.rotate(p.rot);
            ctx.beginPath();
            ctx.ellipse(0, 0, p.size * k, p.size * k * 0.5 * (0.4 + 0.6 * abs(cos(p.flip))), 0, 0, 2 * PI);
            ctx.fill();
            ctx.restore();
        }
        ctx.globalAlpha = 1;
    }

    // Which group is under a point (CSS px)? Topmost layer wins; the wrap and stems count as 'base'.
    const probe = document.createElement('canvas').getContext('2d');
    function toWorld(G, cx, cy) {
        transform(probe, G);
        const m = probe.getTransform().invertSelf().transformPoint(new DOMPoint(cx * dpr, cy * dpr));
        return [m.x / k + VIEW.x0, VIEW.y1 - m.y / k];
    }
    function groupAt(cx, cy) {
        for (let i = LAYERS.length - 1; i >= 0; i--) {
            const L = LAYERS[i];
            if (!L.alpha) continue;
            const [x, y] = toWorld(GROUPS[L.g], cx, cy);
            const b = L.box, a = L.alpha;
            const ix = Math.floor((x - b[0]) * a.R), iy = Math.floor((b[3] - y) * a.R);
            if (ix >= 0 && iy >= 0 && ix < a.w && iy < a.h && a.data[(iy * a.w + ix) * 4 + 3] > 40) return GROUPS[L.g];
        }
        const [x, y] = toWorld(GROUPS.base, cx, cy);
        return x > -4.2 && x < 4.4 && y > -15.5 && y < -5.5 ? GROUPS.base : null;
    }

    function shed(G, count) {
        const [px, py] = G.pivot;
        for (let i = 0; i < count; i++) {
            const a = Math.random() * 2 * PI, speed = 2 + Math.random() * 5;
            petals.push({
                x: px + cos(a) * 1.5, y: py + sin(a) * 1.5, vx: cos(a) * speed, vy: sin(a) * speed + 3,
                rot: Math.random() * PI, spinRate: (Math.random() - 0.5) * 8, flip: Math.random() * PI,
                size: 0.4 + Math.random() * 0.45, c: G.colors[i % G.colors.length], age: 0, life: 2.2 + Math.random(),
            });
        }
        if (petals.length > 160) petals.splice(0, petals.length - 160);
    }

    // Each time the note opens it says something different (never the same line twice in a row)
    const MESSAGES = [
        'terima kasih, ya, sudah kerja keras selalu :]',
        'kamu kesini pasti lagi nunda kerjaan ya. gapapa, aku juga :]',
        'capek? sama. tos dulu ✋',
        'when yh',
        'COSMICCCCCCCCCCCCCCCCCCCCCCCCCCCCC',
        'i love pbp',
        'leave me a message',
    ];
    const message = document.getElementById('bouquet-message');
    let lastMessage = 0;   // the template already shows the first one

    function toggleNote(force) {
        if (!note) return;
        const open = force ?? note.hidden;
        if (open && note.hidden && message) {
            let next = Math.floor(Math.random() * (MESSAGES.length - 1));
            if (next >= lastMessage) next++;              // skip the line that was just shown
            lastMessage = next;
            message.textContent = MESSAGES[next];
        }
        note.hidden = !open;
        canvas.setAttribute('aria-expanded', String(open));
    }

    // Springs: every flower drifts in a breeze, leans away from the pointer and settles after a flick
    function step(now) {
        const dt = Math.min(0.05, (now - last) / 1000 || 0);
        last = now;
        const time = now / 1000;
        const reach = pointer ? Math.max(-1, Math.min(1, (pointer.x - toX(0)) / (canvas.clientWidth / 2))) : 0;
        lean += (reach * -0.06 + sin(time * 0.7) * 0.015 - lean) * Math.min(1, dt * 3);
        for (const G of Object.values(GROUPS)) {
            if (G.name === 'base') continue;
            let push = 0;
            if (pointer) {
                const dx = toX(G.pivot[0]) - pointer.x, dy = toY(G.pivot[1]) - pointer.y;
                push = Math.sign(dx) * Math.exp(-(dx * dx + dy * dy) / (2 * (6 * k) ** 2)) * 0.25;
            }
            const rest = sin(time * 1.1 + G.phase) * 0.06 + push;
            G.spin += ((rest - G.angle) * 40 - G.spin * 5) * dt;
            G.angle += G.spin * dt;
            G.scale += ((G === hovered ? 1.12 : 1) - G.scale) * Math.min(1, dt * 10);
        }
        for (let i = petals.length - 1; i >= 0; i--) {
            const p = petals[i];
            p.age += dt;
            p.vy -= 9 * dt;
            p.vx += sin(time * 4 + p.flip) * 6 * dt;
            p.vx *= 1 - dt * 1.2; p.vy *= 1 - dt * 1.2;
            p.x += p.vx * dt; p.y += p.vy * dt;
            p.rot += p.spinRate * dt; p.flip += dt * 5;
            if (p.age > p.life || p.y < VIEW.y0 - 2) petals.splice(i, 1);
        }
        draw(now);
        frame = requestAnimationFrame(step);
    }

    function run(on) {
        cancelAnimationFrame(frame);
        if (on && !reduceMotion) { last = performance.now(); frame = requestAnimationFrame(step); }
    }

    function local(event) {
        const rect = canvas.getBoundingClientRect();
        return { x: event.clientX - rect.left, y: event.clientY - rect.top };
    }

    canvas.addEventListener('pointermove', event => {
        if (event.pointerType === 'mouse') pointer = local(event);
        if (!ready) return;
        const p = local(event);
        const G = groupAt(p.x, p.y);
        canvas.style.cursor = G ? 'pointer' : 'default';
        hovered = G && G.name !== 'base' ? G : null;    // the wrap doesn't bloom
    });
    canvas.addEventListener('pointerleave', () => { pointer = null; hovered = null; });
    canvas.addEventListener('click', event => {
        if (!ready) return;
        const p = local(event);
        const G = groupAt(p.x, p.y);
        if (!G) return;
        if (G.name === 'base') { toggleNote(); return; }
        if (reduceMotion) return;
        G.spin += (Math.random() < 0.5 ? -1 : 1) * 9;
        G.scale = 1.3;
        shed(G, 12);
    });
    canvas.addEventListener('keydown', event => {
        if (event.key !== 'Enter' && event.key !== ' ') return;
        event.preventDefault();
        toggleNote();
        Object.values(GROUPS).forEach(G => { if (G.name !== 'base') G.spin += (Math.random() - 0.5) * 10; });
    });
    note?.querySelector('[data-close]')?.addEventListener('click', () => { toggleNote(false); canvas.focus(); });

    // Draw only once the footer is near, and animate only while it's on screen
    new IntersectionObserver(entries => {
        const visible = entries[0].isIntersecting;
        if (visible && !started) { started = true; lastWidth = canvas.clientWidth; build(!reduceMotion); }
        run(visible);
    }, { rootMargin: '120px 0px' }).observe(root);

    let resizeTimer = 0, lastWidth = 0;
    new ResizeObserver(() => {
        if (!started || canvas.clientWidth === lastWidth) return;
        lastWidth = canvas.clientWidth;
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => build(false), 150);
    }).observe(canvas);
})();
