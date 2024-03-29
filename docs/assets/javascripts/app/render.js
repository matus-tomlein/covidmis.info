var factCheckIndex = 0;

function renderCarousel(carouselId, factCheckGroups) {
    var factCheckIndex = 0;
    var showGroupGraph = false;

    var previousFactCheck = function () {
        if (factCheckIndex == 0) { factCheckIndex = factCheckGroups.length - 1; }
        else { factCheckIndex -= 1; }
    };
    var nextFactCheck = function () {
        factCheckIndex = (factCheckIndex + 1) % factCheckGroups.length;
    };

    var Carousel = {
        view: function (ctrl) {
            var group = factCheckGroups[factCheckIndex];

            if (showGroupGraph) {
                setTimeout(function () {
                    drawGraph(group.graph_data, 'groupGraph', null, window.innerHeight - 100, false, false);
                }, 100)

                return m('div', {class: 'modal modal-lg active'}, [
                    m('a', {
                        href: '#close',
                        onclick: function () { showGroupGraph = false; return false },
                        class: 'modal-overlay', 'aria-label': (language == 'sk' ? 'Zatvoriť' : 'Close')
                    }),
                    m('div', {class: 'modal-container'},
                        m('div', {class: 'modal-header'},
                            m('a', {
                                href: '#close',
                                onclick: function () { showGroupGraph = false; return false },
                                class: 'btn btn-clear float-right',
                                'aria-label': (language == 'sk' ? 'Zatvoriť' : 'Close')
                            }, ''),
                            m('div', {class: 'modal-title h5 text-ellipsis'}, group.promoted_fact_check.statement)
                        ),
                        m('div', {class: 'modal-body'},
                            m('div', {class: 'content'},
                                m('div', {class: 'column col-12', id: 'groupGraph', style: 'cursor: pointer'})
                            ),
                        ),
                    )
                ]);
            }
            else {
                var verdict = (language == 'sk' ? 'Záver: ' : 'Verdict: ') + group.promoted_fact_check.rating;
                var articles = getGroupArticles(group);

                return [
                    m('div', {'class': 'column col-2', 'style': 'padding-top: 100px'},
                        m('button', {'onclick': previousFactCheck, 'class': 'btn btn-primary btn-action btn-lg'}, m('i', {'class': 'icon icon-arrow-left'}))),

                    m('div', {'class': 'column col-8 mt-2 pt-2'},
                        m('div', {'class': 'hero hero-sm'}, m('div', {'class': 'hero-body'}, [
                            m('h4', { class: 'text-center' },
                                m('a', { href: group.path },
                                    group.promoted_fact_check.statement
                                )
                            ),
                            m('p', { class: 'text-ellipsis' }, group.promoted_fact_check.description),
                            m('p', { class: 'text-center text-large text-ellipsis ' + group.promoted_fact_check.rating_style }, verdict),
                            m('p', { class: 'text-center' },
                                    m('a', { href: group.promoted_fact_check.url, target: '_blank', class: 'btn btn-primary' },
                                        (language == 'sk' ? 'Otvoriť na ' : 'Open at ') + group.promoted_fact_check.domain
                                    ),
                                    m('a', { href: '#', onclick: function () { showGroupGraph = true; return false; }, class: 'btn btn-link' }, [
                                        (language == 'sk' ? ' Preskúmať súvisiace' : ' Explore in graph')
                                    ])
                            ),

                            m('h5', language == 'sk' ? 'Podobné tvrdenia' : 'Similar fact checks'),
                            m('dl', group.fact_checks.filter(function (factCheck) {
                                return factCheck.id != group.promoted_fact_check.id;
                            }).map(function (factCheck) {
                                return [
                                    m('dt', {class: 'text-ellipsis'},
                                        m('a', { href: factCheck.path }, factCheck.statement)
                                    ),
                                    m('dd', {class: 'text-ellipsis ' + factCheck.rating_style}, factCheck.rating),
                                ];
                            }).slice(0, 3)),

                            articles.length > 0 ? [
                                m('h5', language == 'sk' ? 'Články na Webe' : 'Articles found on the Web'),
                                m('dl', articles.map(function (article) {
                                    return [
                                        m('dt', {class: 'text-ellipsis'},
                                            m('a', { href: article.url }, article.title)
                                        ),
                                        m('dd', article.domain)
                                    ];
                                }).slice(0, 3)),

                            ] : null

                        ]))
                    ),

                    m('div', {'class': 'column col-2 text-right', 'style': 'padding-top: 100px'},
                        m('button', {'onclick': nextFactCheck, 'class': 'btn btn-primary btn-action btn-lg'}, m('i', {'class': 'icon icon-arrow-right'}))),

                ];
            }
        }
    };

    m.mount(document.getElementById(carouselId), Carousel);
}

function getGroupArticles(group) {
    var articleMappings = [].concat.apply([], group.fact_checks.map(g => g.article_mappings));
    articleMappings.sort(function (a, b) { return (a.score > b.score) ? -1 : 1; });
    var articles = articleMappings.map(function (articleMapping) { return articleMapping.article; });
    var seen = {};
    return articles.filter(function(item) {
        return seen.hasOwnProperty(item.id) ? false : (seen[item.id] = true);
    });
}

function drawGraph(data, elemId, width, height, zoomOut, freeze) {
    var elem = document.getElementById(elemId);

    var Graph = ForceGraph()(elem);
    if (width) { Graph = Graph.width(width); }
    else { Graph = Graph.width(elem.offsetWidth) }
    if (height) { Graph = Graph.height(height); }

    Graph = Graph
        .graphData(data)
        .nodeLabel('label')
        .nodeColor('group')
        .nodeRelSize(5)
        .linkWidth(1)
        .linkColor('color')
        .nodeCanvasObject((node, ctx, globalScale) => {
            if (node.type == 'group') {
                const label = node.label.substring(0, 100);
                // const fontSize = 12 / globalScale;
                const fontSize = 12;
                ctx.font = `${fontSize}px Sans-Serif`;
                const textWidth = ctx.measureText(label).width;
                const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2); // some padding

                ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
                ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, ...bckgDimensions);

                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillStyle = node.group;
                ctx.fillText(label, node.x, node.y);
            }
            else if (node.type == 'fact_check') {
                ctx.fillStyle = node.group;
                ctx.beginPath(); ctx.arc(node.x, node.y, 7, 0, 2 * Math.PI, false);
                ctx.fill();
            } else {
                ctx.fillStyle = node.group;
                ctx.fillRect(node.x - 6, node.y - 4, 12, 12);
            }
        })
        .d3AlphaDecay(0.01)
        .onNodeHover(node => elem.style.cursor = node ? 'pointer' : null)
        .onNodeClick(node => {
            window.open(node.path, '_blank');
        })
        .onNodeDragEnd(node => {
            node.fx = node.x;
            node.fy = node.y;
        });

    if (zoomOut) { Graph = Graph.zoom(0.5); }
    if (freeze) {
        Graph = Graph
            .enableZoomPanInteraction(false)
            .enablePointerInteraction(false);
        setTimeout(function () {
            Graph.pauseAnimation()
        }, 3000)
    }
}