# Graphiverse

Weekly interactive-data-story site for **02805 — Social Graphs and Interactions**, built by Dimitrios, Andrei & Christos on the shared Marvel Wikipedia network dataset.

Plain HTML/CSS/JS, served by GitHub Pages straight from `main`.

```
index.html              homepage / case-file index
posts/                  one HTML page per weekly post
assets/css/style.css    site styling
assets/js/script.js     small interaction layer
assets/img/             generated figures
scripts/                Python scripts that produce the figures (not deployed)
```

To add a new week's post: drop a page in `posts/`, add a `.case-card` entry linking to it in `index.html`, and drop any generated figures in `assets/img/`.
