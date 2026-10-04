/* Footer: GitHub contribution calendar. One column per week (Sunday on top), five shades by level. */
(function () {
    const graph = document.getElementById('gh-graph');
    const grid = document.getElementById('gh-grid');
    const total = document.getElementById('gh-total');
    if (!graph || !grid) return;

    const MONTH = { month: 'short', timeZone: 'UTC' };
    const DAY = { month: 'short', day: 'numeric', timeZone: 'UTC' };

    // Dates come as YYYY-MM-DD; read them as UTC so the local timezone can't shift a day
    const asDate = value => new Date(value + 'T00:00:00Z');

    let calendar = null;

    // As many whole weeks as fit, newest last, so narrow screens drop the oldest weeks
    function weeksThatFit(weeks) {
        const style = getComputedStyle(grid);
        const gap = parseFloat(style.columnGap) || 0;
        const cell = parseFloat(style.getPropertyValue('--cell-min')) || 9;   // set in work.css, larger on phones
        return Math.max(1, Math.min(weeks, Math.floor((graph.clientWidth + gap) / (cell + gap))));
    }

    function draw(data) {
        const offset = asDate(data.days[0].date).getUTCDay();
        const allWeeks = Math.ceil((offset + data.days.length) / 7);
        const weeks = weeksThatFit(allWeeks);
        const first = allWeeks - weeks;   // first week column on screen
        const cells = [];
        const months = [];

        data.days.forEach((day, i) => {
            const column = Math.floor((offset + i) / 7) - first;
            if (column < 0) return;
            const date = asDate(day.date);
            const name = date.toLocaleDateString('en-US', MONTH);
            // A month is labelled once, over the first column on screen that holds one of its days
            if (!months.length || months[months.length - 1].name !== name) months.push({ column, name });

            const cell = document.createElement('span');
            cell.className = 'gh-d';
            cell.dataset.l = day.level;
            cell.style.gridColumn = column + 1;
            cell.style.setProperty('--c', column);   // fades in column by column on first load
            cell.style.gridRow = (offset + i) % 7 + 2;
            const when = date.toLocaleDateString('en-US', DAY);
            cell.title = day.count
                ? `${day.count} contribution${day.count === 1 ? '' : 's'} on ${when}`
                : `No contributions on ${when}`;
            cells.push(cell);
        });

        // Too close to the next label (a partial first month), the label would overlap it
        if (months.length > 1 && months[1].column - months[0].column < 3) months.shift();
        const labels = months.map(({ column, name }) => {
            const label = document.createElement('span');
            label.className = 'gh-m lbl';
            label.textContent = name;
            label.style.gridColumn = `${column + 1} / span 3`;
            return label;
        });

        const count = data.total.toLocaleString('en-US');
        total.textContent = `${count} contribution${data.total === 1 ? '' : 's'}`;
        grid.style.setProperty('--weeks', weeks);
        grid.setAttribute('aria-label', `${count} GitHub contributions in the last year, by day`);
        grid.replaceChildren(...labels, ...cells);
    }

    let resizeTimer;
    window.addEventListener('resize', () => {
        if (!calendar) return;
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => draw(calendar), 150);
    });

    fetch(graph.dataset.endpoint, { headers: { 'Accept': 'application/json' } })
        .then(response => {
            if (!response.ok) throw new Error(`Status ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (!data.days || !data.days.length) return;
            calendar = data;
            graph.hidden = false;   // shown first, so its width can be measured
            grid.classList.add('is-entering');
            draw(data);
            setTimeout(() => grid.classList.remove('is-entering'), 1500);   // resizes redraw without replaying it
        })
        .catch(error => console.warn('GitHub contributions unavailable:', error));   // the link still works
})();
