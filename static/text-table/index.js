function text_table(rows_, opts) {
    if (!opts) opts = {};
    let hsep = opts.hsep === undefined ? '  ' : opts.hsep;
    let align = opts.align || [];
    let stringLength = opts.stringLength
        || function (s) { return String(s).length; }
    ;
    
    let dotsizes = reduce(rows_, function (acc, row) {
        forEach(row, function (c, ix) {
            let n = dotindex(c);
            if (!acc[ix] || n > acc[ix]) acc[ix] = n;
        });
        return acc;
    }, []);

    // 如果按小数点对齐，修改rows
    let rows = map(rows_, function (row) {
        return map(row, function (c_, ix) {
            let c = String(c_);
            if (align[ix] === '.') {
                let index = dotindex(c);
                let size = dotsizes[ix] + (/\./.test(c) ? 1 : 2)
                    - (stringLength(c) - index)
                ;
                return c + Array(size).join(' ');
            }
            else return c;
        });
    });


    let sizes = reduce(rows, function (acc, row) {
        forEach(row, function (c, ix) {
            let n = stringLength(c);
            if (!acc[ix] || n > acc[ix]) acc[ix] = n;
        });
        return acc;
    }, []);

    return map(rows, function (row) {
        return map(row, function (c, ix) {
            let n = (sizes[ix] - stringLength(c)) || 0;
            let s = Array(Math.max(n + 1, 1)).join(' ');
            if (align[ix] === 'r' || align[ix] === '.') {
                return s + c;
            }
            if (align[ix] === 'c') {
                return Array(Math.ceil(n / 2 + 1)).join(' ')
                    + c + Array(Math.floor(n / 2 + 1)).join(' ')
                ;
            }
            
            return c + s;
        }).join(hsep).replace(/\s+$/, '');
    }).join('\n');
}

function dotindex (c) {
    var m = /\.[^.]*$/.exec(c);
    return m ? m.index + 1 : c.length;
}

function reduce (xs, f, init) {
    if (xs.reduce) return xs.reduce(f, init);
    var i = 0;
    var acc = arguments.length >= 3 ? init : xs[i++];
    for (; i < xs.length; i++) {
        f(acc, xs[i], i);
    }
    return acc;
}

function forEach (xs, f) {
    if (xs.forEach) return xs.forEach(f);
    for (var i = 0; i < xs.length; i++) {
        f.call(xs, xs[i], i);
    }
}

function map (xs, f) {
    if (xs.map) return xs.map(f);
    var res = [];
    for (var i = 0; i < xs.length; i++) {
        res.push(f.call(xs, xs[i], i));
    }
    return res;
}
