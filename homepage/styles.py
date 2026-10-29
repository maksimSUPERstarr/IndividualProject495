"""Общий CSS поверх Bootstrap; пока встроен в учебную функцию page()."""

CSS = """
:root {
    --ink: #172638;
    --muted: #607084;
    --line: #e0e6ed;
    --accent: #245fbb;
    --paper: #f4f6f9;
}
* { box-sizing: border-box; }
body {
    margin: 0; color: var(--ink); background: var(--paper);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 15px; line-height: 1.6;
}
a { color: var(--accent); text-underline-offset: 3px; }
a:hover { color: #163e7b; }
a:focus-visible, input:focus-visible, select:focus-visible,
button:focus-visible { outline: 3px solid #e6ac35; outline-offset: 3px; }
.shell { max-width: 1180px; margin: auto; padding: 0 30px; }
.site-header { background: #fff; border-bottom: 1px solid var(--line); }
.header-inner { min-height: 84px; display: flex; align-items: center;
    justify-content: space-between; gap: 28px; flex-wrap: wrap; }
.brand { display: flex; align-items: center; gap: 12px;
    text-decoration: none; color: var(--ink); font-size: 17px;
    font-weight: 750; line-height: 1.25; }
.brand-mark { width: 36px; height: 36px; display: grid; place-items: center;
    background: #193553; color: #fff; border-radius: 9px; font-size: 17px; }
.brand small { display: block; font-size: 11px; color: var(--muted);
    font-weight: 500; margin-top: 4px; letter-spacing: .06em; }
.site-nav { display: flex; gap: 6px; flex-wrap: wrap; }
.site-nav a { padding: 9px 14px; text-decoration: none;
    color: #526175; border-radius: 7px; font-weight: 600; font-size: 14px; }
.site-nav a:hover, .site-nav a[aria-current] {
    background: #edf3fc; color: #2359a1; }
main.shell { padding-top: 42px; padding-bottom: 64px; min-height: 75vh; }
.eyebrow { color: var(--muted); text-transform: uppercase; font-size: 11px;
    letter-spacing: .12em; font-weight: 700; margin: 0 0 10px; }
h1 { font-size: clamp(27px, 4vw, 36px); font-weight: 720;
    letter-spacing: -.03em; line-height: 1.2; margin: 0 0 14px; }
h2 { font-size: 19px; letter-spacing: -.015em; font-weight: 700; }
h3 { font-size: 16px; font-weight: 700; }
.subtitle { color: var(--muted); max-width: 720px; margin-bottom: 28px; }
.section-title { display: flex; justify-content: space-between;
    align-items: center; gap: 12px; flex-wrap: wrap; margin: 30px 0 15px; }
.section-title h2 { margin: 0; }
.section-title a { font-size: 13px; font-weight: 600; }
.stats { display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 16px; margin: 28px 0 34px; }
.stat, .panel { background: #fff; border: 1px solid var(--line);
    border-radius: 10px; }
.stat { padding: 20px 22px; text-decoration: none; color: var(--ink); }
.stat:hover { border-color: #a7bddc; color: var(--ink); }
.stat strong { font-size: 32px; display: block; line-height: 1.2;
    margin: 5px 0 8px; letter-spacing: -.03em; }
.stat-label { color: var(--muted); font-size: 13px; }
.stat-note { font-size: 12px; color: var(--muted); }
.stat-attention { border-top: 3px solid #d7a334; padding-top: 18px; }
.panel { padding: 24px; margin-bottom: 20px; }
.panel-flush { padding: 0; overflow: hidden; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; margin: 0; }
thead { background: #f9fafc; }
th { color: var(--muted); font-size: 11px; font-weight: 650;
    text-transform: uppercase; letter-spacing: .06em; white-space: nowrap; }
th, td { padding: 17px 22px; border-bottom: 1px solid var(--line);
    text-align: left; vertical-align: middle; }
tbody tr:last-child td { border-bottom: 0; }
tbody tr:hover { background: #fcfdff; }
td a { font-weight: 600; text-decoration: none; }
.secondary { display: block; font-size: 12px; color: var(--muted);
    font-weight: 400; margin-top: 4px; }
.pill { display: inline-block; border-radius: 6px; padding: 4px 9px;
    font-size: 11px; font-weight: 650; white-space: nowrap; }
.pill-green { color: #20624e; background: #e8f4ee; }
.pill-amber { color: #805c13; background: #fcf2d9; }
.pill-gray { color: #606c7c; background: #edf0f4; }
.pill-blue { color: #315c9b; background: #eaf1fc; }
.filters { display: flex; align-items: end; gap: 12px; flex-wrap: wrap;
    margin: 24px 0; }
.filters label { color: #59677a; font-size: 12px; font-weight: 600;
    display: flex; flex-direction: column; gap: 5px; }
.filters input, .filters select { min-height: 42px; background: #fff;
    border: 1px solid #cdd6e1; border-radius: 6px; padding: 8px 12px;
    font: inherit; color: var(--ink); min-width: 190px; }
.filters input { min-width: 250px; }
.action { display: inline-block; border: 1px solid #245fbb;
    border-radius: 6px; background: #245fbb; color: #fff;
    text-decoration: none; padding: 9px 16px; font-size: 13px;
    font-weight: 600; min-height: 42px; }
.action:hover { background: #1c4d9a; color: #fff; }
.action-light { background: #fff; color: #245fbb; }
.two-columns { display: grid; grid-template-columns: 1.4fr 1fr; gap: 20px; }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
dl { margin: 0; }
dt { color: var(--muted); font-size: 12px; margin-bottom: 5px; }
dd { margin-bottom: 20px; font-weight: 550; overflow-wrap: anywhere; }
dd:last-child { margin-bottom: 0; }
.back-link { display: inline-block; font-size: 13px; text-decoration: none;
    margin-bottom: 23px; }
.capacity { min-width: 145px; }
.capacity-label { display: flex; justify-content: space-between;
    font-size: 12px; margin-bottom: 7px; gap: 15px; }
.capacity-bar { height: 5px; border-radius: 4px; background: #e8edf3;
    overflow: hidden; }
.capacity-bar span { display: block; height: 100%; background: #467dbf;
    border-radius: 4px; }
.empty-state { text-align: center; padding: 42px 24px; color: var(--muted); }
.empty-state strong { display: block; color: var(--ink); margin-bottom: 7px; }
.info-note { border-left: 3px solid #aac0dd; padding: 12px 17px;
    color: #5b6a7d; background: #edf2f8; font-size: 13px; margin-top: 24px; }
.site-footer { border-top: 1px solid var(--line); color: var(--muted);
    font-size: 12px; padding: 21px 0; background: #fff; }
.footer-inner { display: flex; justify-content: space-between;
    gap: 12px; flex-wrap: wrap; }
.error-number { font-size: 76px; font-weight: 750; color: #b5c4d7;
    line-height: 1; margin: 18px 0; }
@media (max-width: 800px) {
    .two-columns { grid-template-columns: 1fr; }
    .stats { grid-template-columns: repeat(2, 1fr); }
    .header-inner { padding-top: 18px; padding-bottom: 14px; gap: 15px; }
    .site-nav a { padding: 8px 11px; }
}
@media (max-width: 480px) {
    .shell { padding-left: 18px; padding-right: 18px; }
    main.shell { padding-top: 28px; }
    .stats { gap: 10px; }
    .stat { padding: 15px; }
    .stat strong { font-size: 28px; }
    .detail-grid { grid-template-columns: 1fr; gap: 0; }
    .filters label, .filters input, .filters select { width: 100%;
        min-width: 0; }
    .panel { padding: 19px; }
    .panel-flush { padding: 0; }
    th, td { padding: 14px 16px; }
}
"""
