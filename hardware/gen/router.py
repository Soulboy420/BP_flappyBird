# -*- coding: utf-8 -*-
"""Rasterbasierter Verdrahter (A*) fuer die zweilagige Leiterplatte.

Lage 0 = F.Cu (Signalseite), Lage 1 = B.Cu (Massefläche).
B.Cu wird mit hohen Kosten belegt, damit die Massefläche moeglichst
ungeschnitten bleibt; Durchkontaktierungen kosten zusaetzlich.
"""
import heapq, math
import numpy as np

GRID = 0.2                     # Rasterweite in mm


class Router:
    def __init__(self, w, h, margin=0.6):
        self.w, self.h = w, h
        self.nx = int(round(w / GRID)) + 1
        self.ny = int(round(h / GRID)) + 1
        # feste Sperrflaechen (Rand, Bohrungen, Antennenbereich)
        self.fixed = [np.zeros((self.nx, self.ny), bool) for _ in range(2)]
        m = int(round(margin / GRID))
        for L in self.fixed:
            L[:m, :] = L[-m:, :] = L[:, :m] = L[:, -m:] = True
        # Kupfer je Netz: Liste von (layer, art, geometrie)
        self.copper = []            # (net, layer, kind, data)

    # ---------------------------------------------------------------- Raster
    def _idx(self, x, y):
        return int(round(x / GRID)), int(round(y / GRID))

    def _pos(self, i, j):
        return (round(i * GRID, 3), round(j * GRID, 3))

    def block_rect(self, layer, x1, y1, x2, y2):
        i1, j1 = self._idx(x1, y1)
        i2, j2 = self._idx(x2, y2)
        i1, i2 = max(0, min(i1, i2)), min(self.nx - 1, max(i1, i2))
        j1, j2 = max(0, min(j1, j2)), min(self.ny - 1, max(j1, j2))
        for L in ([self.fixed[layer]] if layer is not None else self.fixed):
            L[i1:i2 + 1, j1:j2 + 1] = True

    def block_circle(self, layer, x, y, r):
        i0, j0 = self._idx(x, y)
        k = int(math.ceil(r / GRID))
        ii = np.arange(max(0, i0 - k), min(self.nx, i0 + k + 1))
        jj = np.arange(max(0, j0 - k), min(self.ny, j0 + k + 1))
        if not len(ii) or not len(jj):
            return
        dx = (ii * GRID - x)[:, None]
        dy = (jj * GRID - y)[None, :]
        mask = dx * dx + dy * dy <= r * r
        for L in ([self.fixed[layer]] if layer is not None else self.fixed):
            L[ii[0]:ii[-1] + 1, jj[0]:jj[-1] + 1] |= mask

    # ---------------------------------------------------------------- Kupfer
    def add_pad(self, net, layers, x, y, w, h):
        self.copper.append((net, layers, 'rect', (x - w, y - h, x + w, y + h)))

    def add_track(self, net, layer, a, b, width):
        self.copper.append((net, (layer,), 'seg', (a, b, width)))

    def add_via(self, net, x, y, dia):
        self.copper.append((net, (0, 1), 'circ', (x, y, dia / 2)))

    # ------------------------------------------------- Hindernisse fuer ein Netz
    def _obstacles(self, net, halfwidth, clear):
        grow = halfwidth + clear
        obs = [self.fixed[0].copy(), self.fixed[1].copy()]
        own = [np.zeros((self.nx, self.ny), bool) for _ in range(2)]
        for cnet, layers, kind, data in self.copper:
            tgt = own if cnet == net else obs
            g = 0.0 if cnet == net else grow
            for L in layers:
                if kind == 'rect':
                    x1, y1, x2, y2 = data
                    self._rect_into(tgt[L], x1 - g, y1 - g, x2 + g, y2 + g)
                elif kind == 'circ':
                    x, y, r = data
                    self._circ_into(tgt[L], x, y, r + g)
                else:
                    a, b, wdt = data
                    self._seg_into(tgt[L], a, b, wdt / 2 + g)
        for L in range(2):
            obs[L] &= ~own[L]
        return obs, own

    def _rect_into(self, arr, x1, y1, x2, y2):
        i1, j1 = self._idx(x1, y1)
        i2, j2 = self._idx(x2, y2)
        i1, i2 = max(0, i1), min(self.nx - 1, i2)
        j1, j2 = max(0, j1), min(self.ny - 1, j2)
        if i1 <= i2 and j1 <= j2:
            arr[i1:i2 + 1, j1:j2 + 1] = True

    def _circ_into(self, arr, x, y, r):
        i0, j0 = self._idx(x, y)
        k = int(math.ceil(r / GRID))
        ii = np.arange(max(0, i0 - k), min(self.nx, i0 + k + 1))
        jj = np.arange(max(0, j0 - k), min(self.ny, j0 + k + 1))
        if not len(ii) or not len(jj):
            return
        dx = (ii * GRID - x)[:, None]
        dy = (jj * GRID - y)[None, :]
        arr[ii[0]:ii[-1] + 1, jj[0]:jj[-1] + 1] |= (dx * dx + dy * dy <= r * r)

    def _seg_into(self, arr, a, b, r):
        n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / (GRID * 0.7)))
        for k in range(n + 1):
            t = k / n
            self._circ_into(arr, a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, r)

    def _via_obstacles(self, net, clear, r=0.4):
        """Raster, in dem eine Durchkontaktierung nicht gesetzt werden darf."""
        grow = r + clear
        bad = self.fixed[0] | self.fixed[1]
        bad = bad.copy()
        own = np.zeros((self.nx, self.ny), bool)
        for cnet, layers, kind, data in self.copper:
            tgt = own if cnet == net else bad
            g = r if cnet == net else grow
            if kind == 'rect':
                x1, y1, x2, y2 = data
                self._rect_into(tgt, x1 - g, y1 - g, x2 + g, y2 + g)
            elif kind == 'circ':
                x, y, rr = data
                self._circ_into(tgt, x, y, rr + g)
            else:
                a, b, wdt = data
                self._seg_into(tgt, a, b, wdt / 2 + g)
        return bad

    # ------------------------------------------------------------------- A*
    NB = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
          (1, 1, 1.4142), (1, -1, 1.4142), (-1, 1, 1.4142), (-1, -1, 1.4142)]

    def route(self, net, targets, halfwidth, clear, via_cost=40.0, back_cost=2.5):
        """targets: Liste von (x, y, layers). Gibt Pfade und Vias zurueck."""
        obs, own = self._obstacles(net, halfwidth, clear)
        viaobs = self._via_obstacles(net, clear)
        starts = [self._idx(t[0], t[1]) for t in targets]
        tlayers = [t[2] for t in targets]
        tree = {(starts[0][0], starts[0][1], 0)}
        paths, vias = [], []
        todo = list(zip(starts[1:], tlayers[1:]))
        while todo:
            goal = None
            best = None
            for g, gl in todo:
                d = min(abs(g[0] - t[0]) + abs(g[1] - t[1]) for t in tree)
                if best is None or d < best:
                    best, goal, glay = d, g, gl
            path = self._astar(obs, own, viaobs, tree, goal, glay, via_cost, back_cost)
            if path is None:
                raise RuntimeError('Netz %s: kein Weg zu %r' % (net, self._pos(*goal)))
            todo.remove((goal, glay))
            segs, vs = self._to_segments(path)
            paths += segs
            vias += vs
            for node in path:
                tree.add(node)
            for a, b, L in segs:
                self._seg_into(own[L], a, b, halfwidth)
            for vx, vy in vs:
                for L in (0, 1):
                    self._circ_into(own[L], vx, vy, 0.4)
        return paths, vias

    def _astar(self, obs, own, viaobs, tree, goal, glay, via_cost, back_cost):
        nx, ny = self.nx, self.ny
        gx, gy = goal
        INF = float('inf')
        dist = {}
        prev = {}
        pq = []
        for node in tree:
            i, j, L = node
            if 0 <= i < nx and 0 <= j < ny and not obs[L][i, j]:
                dist[node] = 0.0
                heapq.heappush(pq, (abs(i - gx) + abs(j - gy), 0.0, node))
        goalset = {(gx, gy, L) for L in glay}
        while pq:
            _, d, node = heapq.heappop(pq)
            if d > dist.get(node, INF):
                continue
            if node in goalset:
                path = [node]
                while node in prev:
                    node = prev[node]
                    path.append(node)
                return path[::-1]
            i, j, L = node
            for di, dj, c in self.NB:
                a, b = i + di, j + dj
                if not (0 <= a < nx and 0 <= b < ny) or obs[L][a, b]:
                    continue
                if di and dj:            # Diagonale nur, wenn beide Nachbarn frei
                    if obs[L][i + di, j] or obs[L][i, j + dj]:
                        continue
                nd = d + c * (1.0 if L == 0 else back_cost)
                nb = (a, b, L)
                if nd < dist.get(nb, INF):
                    dist[nb] = nd
                    prev[nb] = node
                    heapq.heappush(pq, (nd + abs(a - gx) + abs(b - gy), nd, nb))
            M = 1 - L
            if not obs[M][i, j] and not viaobs[i, j]:
                nd = d + via_cost
                nb = (i, j, M)
                if nd < dist.get(nb, INF):
                    dist[nb] = nd
                    prev[nb] = node
                    heapq.heappush(pq, (nd + abs(i - gx) + abs(j - gy), nd, nb))
        return None

    def _to_segments(self, path):
        segs, vias = [], []
        run = [path[0]]
        for node in path[1:]:
            if node[2] != run[-1][2]:
                segs += self._compress(run)
                vias.append(self._pos(node[0], node[1]))
                run = [node]
            else:
                run.append(node)
        segs += self._compress(run)
        return segs, vias

    def _compress(self, run):
        if len(run) < 2:
            return []
        out = []
        L = run[0][2]
        a = run[0]
        d = (run[1][0] - run[0][0], run[1][1] - run[0][1])
        for k in range(1, len(run)):
            nd = (run[k][0] - run[k - 1][0], run[k][1] - run[k - 1][1])
            if nd != d:
                out.append((self._pos(a[0], a[1]), self._pos(run[k - 1][0], run[k - 1][1]), L))
                a, d = run[k - 1], nd
        out.append((self._pos(a[0], a[1]), self._pos(run[-1][0], run[-1][1]), L))
        return [s for s in out if s[0] != s[1]]

    def route_to_via(self, net, pad, halfwidth, clear, viar=0.4, maxlen=8.0):
        """Kuerzeste Stichleitung von einem Pad zu einer zulaessigen Durchkontaktierung."""
        obs, own = self._obstacles(net, halfwidth, clear)
        viaobs = self._via_obstacles(net, clear, viar)
        s = self._idx(*pad)
        if obs[0][s]:
            return None
        INF = float('inf')
        dist = {(s[0], s[1]): 0.0}
        prev = {}
        pq = [(0.0, (s[0], s[1]))]
        lim = maxlen / GRID
        while pq:
            d, node = heapq.heappop(pq)
            if d > dist.get(node, INF):
                continue
            i, j = node
            if d > 1.0 and not viaobs[i, j] and not obs[1][i, j]:
                path = [node]
                while node in prev:
                    node = prev[node]
                    path.append(node)
                path = path[::-1]
                segs = self._compress([(a, b, 0) for a, b in path])
                return segs, self._pos(i, j)
            if d > lim:
                continue
            for di, dj, c in self.NB:
                a, b = i + di, j + dj
                if not (0 <= a < self.nx and 0 <= b < self.ny) or obs[0][a, b]:
                    continue
                if di and dj and (obs[0][i + di, j] or obs[0][i, j + dj]):
                    continue
                nd = d + c
                if nd < dist.get((a, b), INF):
                    dist[(a, b)] = nd
                    prev[(a, b)] = node
                    heapq.heappush(pq, (nd, (a, b)))
        return None

    def _clash_via(self, net, x, y, r=0.4, clear=0.25):
        """True, wenn an (x, y) keine Durchkontaktierung zulaessig ist."""
        vo = self._via_obstacles(net, clear, r)
        i, j = self._idx(x, y)
        if not (0 <= i < self.nx and 0 <= j < self.ny):
            return True
        k = int(math.ceil(r / GRID))
        return bool(vo[max(0, i - k):i + k + 1, max(0, j - k):j + k + 1].any())
