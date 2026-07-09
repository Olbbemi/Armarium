/* code-analyze viewer -- 읽기 전용 SPA. window.DATA(SCHEMA.md 계약)를 7개 뷰로 그린다.
   데이터는 절대 편집하지 않는다(탐색 전용). 정적 에셋이라 어떤 분석 데이터든 이 앱으로 열린다. */
(function () {
  "use strict";

  var STATE = {
    data: null,
    datasets: [],
    datasetIdx: -1,
    view: "overview",
    sub: null,
    searchIndex: []
  };

  var mmCounter = 0;

  var VIEWS = [
    { id: "overview", label: "개요", count: function (d) { return d.modules.length; }, visible: function () { return true; } },
    { id: "structure", label: "구조", count: function (d) { return d.nodes.length; }, visible: function (d) { return d.nodes.length > 0; } },
    { id: "architecture", label: "아키텍처", count: function (d) { return (d.architecture.edges || []).length; }, visible: function (d) { return !!d.architecture; } },
    { id: "flow", label: "플로우", count: function (d) { return d.flows.length; }, visible: function (d) { return d.flows.length > 0; } },
    { id: "coverage", label: "커버리지", count: function (d) { return d.invariants.length; }, visible: function (d) { return d.invariants.length > 0 || d.tests.length > 0; } },
    { id: "externals", label: "외부의존", count: function (d) { return d.externals.length; }, visible: function (d) { return d.externals.length > 0; } },
    { id: "conventions", label: "관례", count: function (d) { return d.conventions ? (d.conventions.naming.length + d.conventions.patterns.length + d.conventions.pitfalls.length) : 0; }, visible: function (d) { return !!d.conventions && (d.conventions.naming.length > 0 || d.conventions.patterns.length > 0 || d.conventions.pitfalls.length > 0 || d.conventions.skips.length > 0); } },
    { id: "datacontracts", label: "데이터계약", count: function (d) { return d.dataContracts.length; }, visible: function (d) { return Array.isArray(d.dataContracts) && d.dataContracts.length > 0; } }
  ];

  // ---------- DOM helper ----------
  function el(tag, attrs, kids) {
    var n = document.createElement(tag);
    if (attrs) {
      for (var k in attrs) {
        if (!Object.prototype.hasOwnProperty.call(attrs, k)) continue;
        var v = attrs[k];
        if (v == null || v === false) continue;
        if (k === "class") n.className = v;
        else if (k === "html") n.innerHTML = v;
        else if (k === "text") n.textContent = v;
        else if (k.slice(0, 2) === "on" && typeof v === "function") n.addEventListener(k.slice(2), v);
        else if (v === true) n.setAttribute(k, "");
        else n.setAttribute(k, v);
      }
    }
    if (kids != null) {
      (Array.isArray(kids) ? kids : [kids]).forEach(function (c) {
        if (c == null || c === false) return;
        n.appendChild(typeof c === "object" ? c : document.createTextNode(String(c)));
      });
    }
    return n;
  }

  function clear(node) { while (node.firstChild) node.removeChild(node.firstChild); }
  function root() { return document.getElementById("view-root"); }

  function nodeSet() {
    var s = new Set();
    (STATE.data.nodes || []).forEach(function (n) { s.add(n.id); });
    return s;
  }
  var _nodeSet = null, _invSet = null, _testSet = null;

  function refNode(id) {
    if (id == null) return el("span", { class: "muted" }, "-");
    if (_nodeSet.has(id)) return el("span", { class: "ref", title: "구조 뷰로 이동", onclick: function () { go("structure", id); } }, id);
    return el("span", { class: "mono muted", title: "매달린 참조(대상 없음)" }, id);
  }
  function refInvariant(id) {
    if (_invSet.has(id)) return el("span", { class: "ref", onclick: function () { go("coverage", id); } }, id);
    return el("span", { class: "mono muted" }, id);
  }
  function refTest(id) {
    if (_testSet.has(id)) return el("span", { class: "ref", onclick: function () { go("coverage", id); } }, id);
    return el("span", { class: "mono muted" }, id);
  }
  function joinRefs(ids, fn) {
    ids = ids || [];
    if (!ids.length) return el("span", { class: "muted" }, "없음");
    var wrap = el("span", { class: "related-list" });
    ids.forEach(function (id) { wrap.appendChild(fn(id)); });
    return wrap;
  }

  // ---------- navigation ----------
  function go(view, sub) {
    location.hash = "#/" + view + (sub != null ? "/" + encodeURIComponent(sub) : "");
  }

  function routeFromHash() {
    if (!STATE.data) return;
    var h = location.hash.replace(/^#\/?/, "");
    var parts = h.split("/").filter(Boolean);
    var view = parts[0] || "overview";
    var sub = parts.length > 1 ? decodeURIComponent(parts.slice(1).join("/")) : null;
    var v = VIEWS.filter(function (x) { return x.id === view && x.visible(STATE.data); })[0];
    if (!v) { view = "overview"; sub = null; }
    STATE.view = view;
    STATE.sub = sub;
    setActiveNav(view);
    renderView();
  }

  function setActiveNav(view) {
    var items = document.querySelectorAll(".nav-item");
    for (var i = 0; i < items.length; i++) {
      items[i].classList.toggle("active", items[i].getAttribute("data-view") === view);
    }
  }

  function buildNav() {
    var nav = document.getElementById("nav");
    clear(nav);
    VIEWS.forEach(function (v) {
      if (!v.visible(STATE.data)) return;
      var item = el("button", { class: "nav-item", "data-view": v.id, type: "button", onclick: function () { go(v.id); } }, [
        el("span", {}, v.label),
        el("span", { class: "nav-count" }, String(v.count(STATE.data)))
      ]);
      nav.appendChild(item);
    });
  }

  // ---------- view rendering ----------
  function viewHead(title, subtitle) {
    return el("div", { class: "view-head" }, [
      el("h1", {}, title),
      subtitle ? el("p", {}, subtitle) : null
    ]);
  }

  function renderView() {
    var r = root();
    clear(r);
    r.scrollTop = 0;
    var d = STATE.data;
    switch (STATE.view) {
      case "overview": renderOverview(r, d); break;
      case "structure": renderStructure(r, d); break;
      case "architecture": renderArchitecture(r, d); break;
      case "flow": renderFlow(r, d); break;
      case "coverage": renderCoverage(r, d); break;
      case "externals": renderExternals(r, d); break;
      case "conventions": renderConventions(r, d); break;
      case "datacontracts": renderDataContracts(r, d); break;
      default: renderOverview(r, d);
    }
  }

  function stat(num, label) {
    return el("div", { class: "stat" }, [
      el("div", { class: "stat-num" }, String(num)),
      el("div", { class: "stat-label" }, label)
    ]);
  }

  function renderOverview(r, d) {
    r.appendChild(viewHead("개요", (d.meta.target || "") + " -- as-built 구조 요약"));
    var grid = el("div", { class: "stat-grid" }, [
      stat(d.nodes.length, "노드"),
      stat(d.modules.length, "모듈"),
      stat(d.flows.length, "플로우"),
      stat(d.invariants.length, "불변식"),
      stat(d.tests.length, "테스트"),
      stat(d.externals.length, "외부 의존")
    ]);
    r.appendChild(grid);

    var modCard = el("div", { class: "card" }, [el("h2", {}, ["모듈", el("span", { class: "count-badge" }, "(" + d.modules.length + ")")])]);
    if (d.modules.length) {
      var tbl = el("table", { class: "grid" }, [
        el("thead", {}, el("tr", {}, [el("th", {}, "모듈"), el("th", {}, "레이어"), el("th", {}, "역할")])),
        el("tbody", {}, d.modules.map(function (m) {
          return el("tr", {}, [
            el("td", {}, el("span", { class: "mono" }, m.name || m.id)),
            el("td", {}, el("span", { class: "tag layer-" + (m.layer || "") }, m.layer || "-")),
            el("td", {}, m.role || "-")
          ]);
        }))
      ]);
      modCard.appendChild(el("div", { class: "table-scroll" }, tbl));
    } else {
      modCard.appendChild(el("p", { class: "muted" }, "모듈 정보 없음"));
    }
    r.appendChild(modCard);

    var gaps = d.invariants.filter(function (i) { return !(i.coveredBy && i.coveredBy.length); });
    if (gaps.length) {
      var gc = el("div", { class: "card" }, [el("h2", {}, "테스트 미커버 불변식")]);
      gc.appendChild(el("div", { class: "table-scroll" }, el("table", { class: "grid" }, [
        el("thead", {}, el("tr", {}, [el("th", {}, "불변식"), el("th", {}, "범위"), el("th", {}, "진술")])),
        el("tbody", {}, gaps.map(function (i) {
          return el("tr", { class: "gap-row" }, [el("td", {}, el("span", { class: "mono" }, i.id)), el("td", {}, i.scope || "-"), el("td", {}, i.statement || "-")]);
        }))
      ])));
      r.appendChild(gc);
    }
  }

  function renderStructure(r, d) {
    r.appendChild(viewHead("구조", "모듈 -> 노드. 노드를 골라 타입/함수/관계를 본다."));
    if (!d.nodes.length) { r.appendChild(el("div", { class: "empty-state" }, "구조 노드가 없습니다.")); return; }

    var layout = el("div", { class: "struct-layout" });
    var tree = el("div", { class: "tree" });
    // group nodes by module
    var byMod = {};
    d.nodes.forEach(function (n) { (byMod[n.module] = byMod[n.module] || []).push(n); });
    d.modules.forEach(function (m) { if (!byMod[m.id]) return; addTreeModule(tree, m.name || m.id, byMod[m.id]); });
    // nodes whose module isn't in modules[]
    Object.keys(byMod).forEach(function (mid) {
      if (!d.modules.some(function (m) { return m.id === mid; })) addTreeModule(tree, mid, byMod[mid]);
    });
    layout.appendChild(tree);

    var detail = el("div", { class: "node-detail card", id: "node-detail" });
    layout.appendChild(detail);
    r.appendChild(layout);

    var selId = STATE.sub && _nodeSet.has(STATE.sub) ? STATE.sub : d.nodes[0].id;
    renderNodeDetail(detail, selId);
    markActiveTreeNode(selId);

    function addTreeModule(container, name, nodes) {
      var mod = el("div", { class: "tree-module" }, [el("div", { class: "tree-module-name" }, name)]);
      nodes.forEach(function (n) {
        mod.appendChild(el("button", { class: "tree-node", type: "button", "data-node": n.id, onclick: function () { go("structure", n.id); } }, [
          el("span", {}, n.id), el("span", { class: "tn-kind" }, "  " + (n.kind || ""))
        ]));
      });
      container.appendChild(mod);
    }
  }

  function markActiveTreeNode(id) {
    var btns = document.querySelectorAll(".tree-node");
    for (var i = 0; i < btns.length; i++) btns[i].classList.toggle("active", btns[i].getAttribute("data-node") === id);
  }

  function renderNodeDetail(container, id) {
    clear(container);
    var n = STATE.data.nodes.filter(function (x) { return x.id === id; })[0];
    if (!n) { container.appendChild(el("p", { class: "muted" }, "노드를 찾을 수 없습니다.")); return; }

    container.appendChild(el("h2", {}, [n.id, el("span", { class: "tag kind" }, n.kind || "")]));
    container.appendChild(el("div", { class: "nd-path" }, n.path || ""));
    if (n.role) container.appendChild(el("p", {}, n.role));

    (n.types || []).forEach(function (t) {
      var block = el("div", { style: "margin-top:14px" });
      var head = el("div", {}, [
        el("strong", {}, t.name || ""),
        el("span", { class: "tag kind", style: "margin-left:6px" }, t.kind || "")
      ]);
      (t.bases || []).forEach(function (b) { head.appendChild(el("span", { class: "tag" }, ": " + b)); });
      block.appendChild(head);
      if (t.role) block.appendChild(el("div", { class: "muted", style: "margin:2px 0 8px" }, t.role));

      (t.members || []).forEach(function (mem) {
        block.appendChild(el("div", { class: "member-row" }, [
          el("span", { class: "m-kind" }, mem.kind || ""),
          el("span", { class: "sig" }, mem.sig || "")
        ]));
      });
      if (t.invariants && t.invariants.length) {
        block.appendChild(el("div", { style: "margin-top:6px" }, [el("span", { class: "rel-label" }, "불변식  "), joinRefs(t.invariants, refInvariant)]));
      }
      if (t.exceptions && t.exceptions.length) {
        var ex = el("div", { style: "margin-top:4px" }, [el("span", { class: "rel-label" }, "예외  ")]);
        t.exceptions.forEach(function (e) { ex.appendChild(el("span", { class: "tag exc" }, e)); });
        block.appendChild(ex);
      }
      container.appendChild(block);
    });

    if (n.functions && n.functions.length) {
      container.appendChild(el("h2", { style: "margin-top:16px;font-size:14px" }, "함수"));
      n.functions.forEach(function (f) {
        var fb = el("div", { class: "member-row", style: "flex-direction:column;align-items:flex-start;gap:2px" }, [
          el("span", { class: "sig" }, f.signature || ""),
          f.role ? el("span", { class: "muted" }, f.role) : null
        ]);
        if (f.exceptions && f.exceptions.length) {
          var ex2 = el("span", {});
          f.exceptions.forEach(function (e) { ex2.appendChild(el("span", { class: "tag exc" }, e)); });
          fb.appendChild(ex2);
        }
        container.appendChild(fb);
      });
    }

    if (n.related && n.related.length) {
      container.appendChild(el("h2", { style: "margin-top:16px;font-size:14px" }, "관계"));
      var rel = el("div", { class: "related-list" });
      n.related.forEach(function (rr) {
        rel.appendChild(el("span", { class: "rel-label" }, rr.relation || "->"));
        rel.appendChild(refNode(rr.targetId));
      });
      container.appendChild(rel);
    }
  }

  function renderArchitecture(r, d) {
    var a = d.architecture || {};
    r.appendChild(viewHead("아키텍처", "진입점, 경계(포트), 의존 그래프, 호출 그래프."));

    if (a.entryPoints && a.entryPoints.length) {
      var epc = el("div", { class: "card" }, [el("h2", {}, "진입점")]);
      epc.appendChild(el("div", { class: "table-scroll" }, el("table", { class: "grid" }, [
        el("thead", {}, el("tr", {}, [el("th", {}, "노드"), el("th", {}, "표면")])),
        el("tbody", {}, a.entryPoints.map(function (e) { return el("tr", {}, [el("td", {}, refNode(e.id)), el("td", {}, el("span", { class: "mono" }, e.surface || "-"))]); }))
      ])));
      r.appendChild(epc);
    }

    if (a.entrySurfaceMap && a.entrySurfaceMap.length) {
      var esc = el("div", { class: "card" }, [el("h2", {}, "진입 표면 -> 핸들러")]);
      esc.appendChild(el("div", { class: "table-scroll" }, el("table", { class: "grid" }, [
        el("thead", {}, el("tr", {}, [el("th", {}, "표면"), el("th", {}, "핸들러")])),
        el("tbody", {}, a.entrySurfaceMap.map(function (m) { return el("tr", {}, [el("td", {}, el("span", { class: "mono" }, m.surface || "-")), el("td", {}, refNode(m.handlerId))]); }))
      ])));
      r.appendChild(esc);
    }

    if (a.ports && a.ports.length) {
      var pc = el("div", { class: "card" }, [el("h2", {}, "포트 <- 구현")]);
      pc.appendChild(el("div", { class: "table-scroll" }, el("table", { class: "grid" }, [
        el("thead", {}, el("tr", {}, [el("th", {}, "포트"), el("th", {}, "구현")])),
        el("tbody", {}, a.ports.map(function (p) { return el("tr", {}, [el("td", {}, el("span", { class: "mono" }, p.port || "-")), el("td", {}, joinRefs(p.implIds, refNode))]); }))
      ])));
      r.appendChild(pc);
    }

    if (a.mermaid) {
      var dc = el("div", { class: "card" }, [el("h2", {}, "의존 그래프")]);
      dc.appendChild(diagramBlock("모듈 의존", a.mermaid, { collapsed: false }));
      r.appendChild(dc);
    }

    if (d.callgraph && d.callgraph.graphs && d.callgraph.graphs.length) {
      var cg = el("div", { class: "card" }, [el("h2", {}, ["호출 그래프", el("span", { class: "count-badge" }, "(" + d.callgraph.graphs.length + ")")])]);
      d.callgraph.graphs.forEach(function (g) {
        cg.appendChild(diagramBlock(g.label || g.id, g.mermaid, { collapsed: !!g.defaultCollapsed }));
      });
      r.appendChild(cg);
    }
  }

  function renderFlow(r, d) {
    r.appendChild(viewHead("플로우", "트리거 + 생명주기에 앵커된 end-to-end 경로."));
    d.flows.forEach(function (f) {
      var card = el("div", { class: "card flow-card", id: "flow-" + f.id });
      card.appendChild(el("h2", {}, f.id));
      var meta = el("div", { class: "flow-meta" }, [
        el("div", { class: "fm-item" }, [el("span", { class: "fm-label" }, "트리거"), f.trigger || "-"]),
        el("div", { class: "fm-item" }, [el("span", { class: "fm-label" }, "생명주기"), f.lifecycle || "-"])
      ]);
      card.appendChild(meta);
      if (f.steps && f.steps.length) {
        card.appendChild(el("ol", { class: "steps" }, f.steps.map(function (s) { return el("li", {}, s); })));
      }
      if (f.relatedNodes && f.relatedNodes.length) {
        card.appendChild(el("div", { style: "margin-bottom:10px" }, [el("span", { class: "rel-label" }, "관여 노드  "), joinRefs(f.relatedNodes, refNode)]));
      }
      if (f.mermaid) card.appendChild(diagramBlock("시퀀스 다이어그램", f.mermaid, { collapsed: false }));
      r.appendChild(card);
    });
    if (STATE.sub) {
      var target = document.getElementById("flow-" + STATE.sub);
      if (target) target.scrollIntoView({ block: "start" });
    }
  }

  function renderCoverage(r, d) {
    r.appendChild(viewHead("커버리지", "불변식 <-> 테스트 조인. 미커버 불변식이 공백이다."));

    var ic = el("div", { class: "card" }, [el("h2", {}, ["불변식", el("span", { class: "count-badge" }, "(" + d.invariants.length + ")")])]);
    ic.appendChild(el("div", { class: "table-scroll" }, el("table", { class: "grid" }, [
      el("thead", {}, el("tr", {}, [el("th", {}, "ID"), el("th", {}, "진술"), el("th", {}, "범위"), el("th", {}, "커버 테스트")])),
      el("tbody", {}, d.invariants.map(function (i) {
        var covered = i.coveredBy && i.coveredBy.length;
        return el("tr", { class: covered ? "" : "gap-row", id: "inv-" + i.id }, [
          el("td", {}, el("span", { class: "mono" }, i.id)),
          el("td", {}, i.statement || "-"),
          el("td", {}, i.scope || "-"),
          el("td", {}, covered ? joinRefs(i.coveredBy, refTest) : el("span", { class: "cov-no" }, "미커버"))
        ]);
      }))
    ])));
    r.appendChild(ic);

    if (d.tests.length) {
      var tc = el("div", { class: "card" }, [el("h2", {}, ["테스트", el("span", { class: "count-badge" }, "(" + d.tests.length + ")")])]);
      tc.appendChild(el("div", { class: "table-scroll" }, el("table", { class: "grid" }, [
        el("thead", {}, el("tr", {}, [el("th", {}, "ID"), el("th", {}, "이름"), el("th", {}, "대상"), el("th", {}, "커버 불변식")])),
        el("tbody", {}, d.tests.map(function (t) {
          return el("tr", { id: "test-row-" + t.id }, [
            el("td", {}, el("span", { class: "mono" }, t.id)),
            el("td", {}, t.name || "-"),
            el("td", {}, refNode(t.target)),
            el("td", {}, joinRefs(t.covers, refInvariant))
          ]);
        }))
      ])));
      r.appendChild(tc);
    }

    if (STATE.sub) {
      var tgt = document.getElementById("inv-" + STATE.sub) || document.getElementById("test-row-" + STATE.sub);
      if (tgt) { tgt.scrollIntoView({ block: "center" }); tgt.style.outline = "2px solid var(--accent)"; }
    }
  }

  function renderExternals(r, d) {
    r.appendChild(viewHead("외부 의존", "외부 라이브러리 + 버전 + 경계(어댑터/포트)."));
    var card = el("div", { class: "card" });
    card.appendChild(el("div", { class: "table-scroll" }, el("table", { class: "grid" }, [
      el("thead", {}, el("tr", {}, [el("th", {}, "이름"), el("th", {}, "버전"), el("th", {}, "어댑터"), el("th", {}, "벤더링"), el("th", {}, "포트")])),
      el("tbody", {}, d.externals.map(function (e) {
        return el("tr", {}, [
          el("td", {}, el("strong", {}, e.name || "-")),
          el("td", {}, el("span", { class: "mono" }, e.version || "-")),
          el("td", {}, e.adapter ? refNode(e.adapter) : el("span", { class: "muted" }, "-")),
          el("td", {}, e.vendored ? el("span", { class: "tag" }, "vendored") : el("span", { class: "muted" }, "외부")),
          el("td", {}, e.port ? el("span", { class: "mono" }, e.port) : el("span", { class: "muted" }, "-"))
        ]);
      }))
    ])));
    r.appendChild(card);
  }

  function renderConventions(r, d) {
    var c = d.conventions || {};
    r.appendChild(viewHead("관례", "프로젝트 고유 네이밍 / 패턴 / 함정 + 분석 스킵 기록."));

    if (c.naming && c.naming.length) {
      var nc = el("div", { class: "card" }, [el("h2", {}, ["네이밍 규칙", el("span", { class: "count-badge" }, "(" + c.naming.length + ")")])]);
      nc.appendChild(el("div", { class: "table-scroll" }, el("table", { class: "grid" }, [
        el("thead", {}, el("tr", {}, [el("th", {}, "범위"), el("th", {}, "규칙"), el("th", {}, "예")])),
        el("tbody", {}, c.naming.map(function (n) {
          return el("tr", {}, [
            el("td", {}, el("span", { class: "tag" }, n.scope || "-")),
            el("td", {}, n.rule || "-"),
            el("td", {}, n.example ? el("span", { class: "mono" }, n.example) : el("span", { class: "muted" }, "-"))
          ]);
        }))
      ])));
      r.appendChild(nc);
    }

    if (c.patterns && c.patterns.length) {
      var pc = el("div", { class: "card" }, [el("h2", {}, ["반복 패턴 / 이디엄", el("span", { class: "count-badge" }, "(" + c.patterns.length + ")")])]);
      c.patterns.forEach(function (p) {
        pc.appendChild(el("div", { class: "conv-item" }, [
          el("div", {}, el("strong", {}, p.name || "-")),
          p.description ? el("div", { class: "muted", style: "margin:2px 0 6px" }, p.description) : null,
          (p.relatedNodes && p.relatedNodes.length) ? el("div", {}, [el("span", { class: "rel-label" }, "관련 노드  "), joinRefs(p.relatedNodes, refNode)]) : null
        ]));
      });
      r.appendChild(pc);
    }

    if (c.pitfalls && c.pitfalls.length) {
      var fc = el("div", { class: "card" }, [el("h2", {}, ["함정 (gotchas)", el("span", { class: "count-badge" }, "(" + c.pitfalls.length + ")")])]);
      c.pitfalls.forEach(function (p) {
        fc.appendChild(el("div", { class: "conv-item" }, [
          el("div", {}, p.statement || "-"),
          (p.relatedNodes && p.relatedNodes.length) ? el("div", { style: "margin-top:4px" }, [el("span", { class: "rel-label" }, "관련 노드  "), joinRefs(p.relatedNodes, refNode)]) : null
        ]));
      });
      r.appendChild(fc);
    }

    if (c.skips && c.skips.length) {
      var sc = el("div", { class: "card" }, [el("h2", {}, ["분석 스킵 기록", el("span", { class: "count-badge" }, "(" + c.skips.length + ")")])]);
      sc.appendChild(el("div", { class: "table-scroll" }, el("table", { class: "grid" }, [
        el("thead", {}, el("tr", {}, [el("th", {}, "경로 / 패턴"), el("th", {}, "사유")])),
        el("tbody", {}, c.skips.map(function (s) {
          return el("tr", {}, [el("td", {}, el("span", { class: "mono" }, s.path || "-")), el("td", {}, s.reason || "-")]);
        }))
      ])));
      r.appendChild(sc);
    }

    if (!(c.naming && c.naming.length) && !(c.patterns && c.patterns.length) && !(c.pitfalls && c.pitfalls.length) && !(c.skips && c.skips.length)) {
      r.appendChild(el("div", { class: "empty-state" }, "기록된 관례가 없습니다."));
    }
  }

  function renderDataContracts(r, d) {
    r.appendChild(viewHead("데이터 계약", "영속/설정 스키마."));
    d.dataContracts.forEach(function (c) {
      var card = el("div", { class: "card" }, [el("h2", {}, [c.name || "-", el("span", { class: "tag kind" }, c.kind || "")])]);
      if (c.fields && c.fields.length) {
        card.appendChild(el("div", { class: "table-scroll" }, el("table", { class: "grid" }, [
          el("thead", {}, el("tr", {}, [el("th", {}, "필드"), el("th", {}, "타입"), el("th", {}, "제약")])),
          el("tbody", {}, c.fields.map(function (f) {
            return el("tr", {}, [el("td", {}, el("span", { class: "mono" }, f.name || "-")), el("td", {}, el("span", { class: "mono" }, f.type || "-")), el("td", {}, f.constraints || "-")]);
          }))
        ])));
      }
      r.appendChild(card);
    });
  }

  // ---------- mermaid ----------
  function initMermaid() {
    if (!window.mermaid) return;
    try {
      window.mermaid.initialize({
        startOnLoad: false,
        securityLevel: "strict",
        theme: resolveTheme() === "dark" ? "dark" : "default",
        flowchart: { useMaxWidth: true },
        sequence: { useMaxWidth: true }
      });
    } catch (e) { /* noop */ }
  }

  function diagramBlock(label, src, opts) {
    opts = opts || {};
    var details = el("details", { class: "collapsible" });
    if (!opts.collapsed) details.setAttribute("open", "");
    details.appendChild(el("summary", {}, label));
    var dia = el("div", { class: "diagram" });
    details.appendChild(el("div", { class: "collapsible-body" }, dia));
    var done = false;
    function doRender() { if (done) return; done = true; renderMermaid(dia, src); }
    details.addEventListener("toggle", function () { if (details.open) doRender(); });
    if (details.open) setTimeout(doRender, 0);
    return details;
  }

  function renderMermaid(container, src) {
    if (!window.mermaid) { showDiagramError(container, "mermaid 라이브러리를 로드하지 못했습니다."); return; }
    var id = "mmd-" + (++mmCounter);
    try {
      var res = window.mermaid.render(id, src);
      if (res && typeof res.then === "function") {
        res.then(function (out) { container.innerHTML = out.svg; }).catch(function (e) { showDiagramError(container, e); });
      } else if (res && res.svg) {
        container.innerHTML = res.svg;
      }
    } catch (e) { showDiagramError(container, e); }
  }

  function showDiagramError(container, e) {
    var msg = (e && e.message) ? e.message : String(e);
    clear(container);
    container.appendChild(el("div", { class: "diagram-error" }, "다이어그램 렌더 실패: " + msg));
  }

  // ---------- search ----------
  function buildSearchIndex() {
    var d = STATE.data, idx = [];
    d.nodes.forEach(function (n) { idx.push({ kind: "노드", name: n.id, sub: n.role || n.path || "", go: function () { go("structure", n.id); } }); });
    d.modules.forEach(function (m) { idx.push({ kind: "모듈", name: m.name || m.id, sub: m.role || "", go: function () { go("architecture"); } }); });
    d.flows.forEach(function (f) { idx.push({ kind: "플로우", name: f.id, sub: f.trigger || "", go: function () { go("flow", f.id); } }); });
    d.invariants.forEach(function (i) { idx.push({ kind: "불변식", name: i.id, sub: i.statement || "", go: function () { go("coverage", i.id); } }); });
    d.tests.forEach(function (t) { idx.push({ kind: "테스트", name: t.id, sub: t.name || "", go: function () { go("coverage", t.id); } }); });
    d.externals.forEach(function (e) { idx.push({ kind: "외부", name: e.name, sub: (e.version || "") + " " + (e.adapter || ""), go: function () { go("externals"); } }); });
    if (d.conventions) {
      (d.conventions.patterns || []).forEach(function (p) { idx.push({ kind: "관례", name: p.name || "", sub: p.description || "", go: function () { go("conventions"); } }); });
      (d.conventions.pitfalls || []).forEach(function (p) { idx.push({ kind: "함정", name: trunc(p.statement || "", 40), sub: "", go: function () { go("conventions"); } }); });
    }
    STATE.searchIndex = idx;
  }

  function setupSearch() {
    var input = document.getElementById("search");
    var box = document.getElementById("search-results");
    var activeIdx = -1, current = [];

    function close() { box.hidden = true; activeIdx = -1; }
    function paint(results) {
      current = results; activeIdx = -1;
      clear(box);
      if (!results.length) { box.appendChild(el("div", { class: "search-empty" }, "결과 없음")); box.hidden = false; return; }
      results.forEach(function (rz, i) {
        box.appendChild(el("div", { class: "search-result", "data-i": i, onclick: function () { pick(rz); } }, [
          el("span", { class: "sr-kind" }, rz.kind),
          el("span", { class: "sr-name" }, rz.name),
          rz.sub ? el("span", { class: "sr-sub" }, trunc(rz.sub, 60)) : null
        ]));
      });
      box.hidden = false;
    }
    function pick(rz) { input.value = ""; close(); rz.go(); }

    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase();
      if (!q) { close(); return; }
      var res = STATE.searchIndex.filter(function (it) {
        return (it.name || "").toLowerCase().indexOf(q) >= 0 || (it.sub || "").toLowerCase().indexOf(q) >= 0;
      }).slice(0, 40);
      paint(res);
    });
    input.addEventListener("keydown", function (e) {
      if (box.hidden) return;
      if (e.key === "ArrowDown") { e.preventDefault(); activeIdx = Math.min(activeIdx + 1, current.length - 1); highlight(); }
      else if (e.key === "ArrowUp") { e.preventDefault(); activeIdx = Math.max(activeIdx - 1, 0); highlight(); }
      else if (e.key === "Enter") { if (activeIdx >= 0 && current[activeIdx]) pick(current[activeIdx]); }
      else if (e.key === "Escape") { close(); }
    });
    function highlight() {
      var rows = box.querySelectorAll(".search-result");
      for (var i = 0; i < rows.length; i++) rows[i].classList.toggle("active", i === activeIdx);
      if (rows[activeIdx]) rows[activeIdx].scrollIntoView({ block: "nearest" });
    }
    document.addEventListener("click", function (e) { if (!box.contains(e.target) && e.target !== input) close(); });
  }
  function trunc(s, n) { s = String(s); return s.length > n ? s.slice(0, n - 1) + "..." : s; }

  // ---------- theme ----------
  function resolveTheme() {
    var t = document.documentElement.getAttribute("data-theme");
    if (t) return t;
    return (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) ? "dark" : "light";
  }
  function setupTheme() {
    var saved = null;
    try { saved = localStorage.getItem("ca-viewer-theme"); } catch (e) { /* file:// may block */ }
    if (saved) document.documentElement.setAttribute("data-theme", saved);
    document.getElementById("theme-toggle").addEventListener("click", function () {
      var next = resolveTheme() === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      try { localStorage.setItem("ca-viewer-theme", next); } catch (e) { /* noop */ }
      initMermaid();
      if (STATE.data) renderView();
    });
  }

  // ---------- dataset loading ----------
  function loadData(path, ok, fail) {
    try { window.DATA = undefined; } catch (e) { /* noop */ }
    var prev = document.getElementById("__data_script");
    if (prev) prev.parentNode.removeChild(prev);
    var s = document.createElement("script");
    s.id = "__data_script";
    s.src = path;
    s.onload = function () {
      if (window.DATA && typeof window.DATA === "object") ok(normalize(window.DATA));
      else fail(new Error("window.DATA 누락: " + path));
    };
    s.onerror = function () { fail(new Error("로드 실패: " + path)); };
    document.body.appendChild(s);
  }

  // 조건부/누락 키를 뷰어가 안전하게 다루도록 항상-배열 키를 보정한다(데이터를 바꾸지 않고 부재만 채움).
  function normalize(d) {
    d.meta = d.meta || {};
    d.modules = d.modules || [];
    d.nodes = d.nodes || [];
    d.architecture = d.architecture || { edges: [] };
    d.flows = d.flows || [];
    d.invariants = d.invariants || [];
    d.tests = d.tests || [];
    d.externals = d.externals || [];
    d.dataContracts = Array.isArray(d.dataContracts) ? d.dataContracts : [];
    if (d.conventions) {
      d.conventions.naming = d.conventions.naming || [];
      d.conventions.patterns = d.conventions.patterns || [];
      d.conventions.pitfalls = d.conventions.pitfalls || [];
      d.conventions.skips = d.conventions.skips || [];
    }
    return d;
  }

  function buildPicker() {
    var wrap = document.getElementById("dataset-wrap");
    var sel = document.getElementById("dataset-picker");
    if (STATE.datasets.length <= 1) { wrap.hidden = true; return; }
    wrap.hidden = false;
    clear(sel);
    STATE.datasets.forEach(function (ds, i) {
      sel.appendChild(el("option", { value: String(i) }, ds.branch || ("dataset " + (i + 1))));
    });
    sel.value = String(STATE.datasetIdx >= 0 ? STATE.datasetIdx : 0);
    sel.onchange = function () { selectDataset(parseInt(sel.value, 10)); };
  }

  function selectDataset(idx) {
    var ds = STATE.datasets[idx];
    if (!ds) { showFatal("사용 가능한 데이터셋이 없습니다."); return; }
    STATE.datasetIdx = idx;
    loadData(ds.path, function (data) {
      hideBanner();
      STATE.data = data;
      STATE.dataset = ds;
      _nodeSet = nodeSet();
      _invSet = new Set(data.invariants.map(function (i) { return i.id; }));
      _testSet = new Set(data.tests.map(function (t) { return t.id; }));
      onDataLoaded();
      buildPicker();
    }, function (err) {
      // 자가치유: 로드 실패한 항목을 목록에서 제거하고 다음 것을 시도
      STATE.datasets.splice(idx, 1);
      if (STATE.datasets.length) { buildPicker(); selectDataset(Math.min(idx, STATE.datasets.length - 1)); }
      else showFatal(err.message);
    });
  }

  function onDataLoaded() {
    var d = STATE.data;
    document.getElementById("target-name").textContent = d.meta.target || "-";
    document.getElementById("branch-name").textContent = d.meta.branch || "-";
    var lc = document.getElementById("lang-chip");
    if (d.meta.language) { lc.textContent = d.meta.language; lc.hidden = false; } else lc.hidden = true;
    document.title = (d.meta.target || "code-analyze") + " -- viewer";
    buildNav();
    buildSearchIndex();
    routeFromHash();
  }

  function showFatal(msg) {
    var r = root();
    clear(r);
    r.appendChild(el("div", { class: "empty-state" }, [el("p", {}, "데이터를 표시할 수 없습니다."), el("p", { class: "mono" }, msg)]));
  }
  function showBanner(msg) { var b = document.getElementById("error-banner"); b.textContent = msg; b.hidden = false; }
  function hideBanner() { document.getElementById("error-banner").hidden = true; }

  // ---------- boot ----------
  function boot() {
    setupTheme();
    initMermaid();
    setupSearch();
    window.addEventListener("hashchange", routeFromHash);

    var params = new URLSearchParams(location.search);
    var override = params.get("data");
    if (override) {
      STATE.datasets = [{ branch: params.get("branch") || "data", path: override }];
      buildPicker();
      selectDataset(0);
      return;
    }

    var man = (!window.__manifestError && Array.isArray(window.MANIFEST)) ? window.MANIFEST.slice() : [];
    STATE.datasets = man.filter(function (m) { return m && m.path; });
    if (!STATE.datasets.length) {
      showFatal("로드할 데이터셋이 없습니다 (manifest.js 부재 또는 비어있음).");
      return;
    }
    buildPicker();
    selectDataset(0);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
