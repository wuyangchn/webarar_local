/*
// Calculation functions such as regression method, age calculation, etc...
*/

function arr_sum(array) {
    // sum of elements of a array
    if (Array.isArray(array)) {
        return array.reduce((acc, curr) => acc + curr, 0); // 计算数组元素的总和
    } else {
        console.error('array is not an array');
        return array;
    }
}

function arr_sub(...args) {
    // subtraction of arrays, array1 - array2 - ...args
    let data = numeric.transpose(args);
    return data.map(value => value.reduce((acc, curr, index) => index === 0 ? curr : acc - curr, 0));
}

function arr_add(...args) {
    // subtraction of arrays, array1 - array2 - ...args
    let data = numeric.transpose(args);
    return data.map(value => value.reduce((acc, curr, index) => acc + curr, 0));
}

function arr_div(...args) {
    // subtraction of arrays, array1 - array2 - ...args
    let data = numeric.transpose(args);
    return data.map(value => value.reduce((acc, curr, index) => index === 0 ? curr : acc / curr, 1));
}

function arr_mul(...args) {
    // subtraction of arrays, array1 - array2 - ...args
    let data = numeric.transpose(args);
    return data.map(value => value.reduce((acc, curr, index) => index === 0 ? curr : acc * curr, 1));
}

function arr_pow(array, power) {
    // array with all elements powered
    return array.map(value => Array.isArray(value)?arr_pow(value, power):Math.pow(value, power));
}

function arr_multiply_by_number(array, f) {
    if (Array.isArray(array)) {
        return array.map(value => arr_multiply_by_number(value, f))
    } else {
        return array * f
    }
}

function arr_mean(array) {
    // mean of elements of a array
    if (array.length === 0) {
        return NaN; // 如果数组为空，返回 NaN
    }
    const sum = arr_sum(array);
    return sum / array.length; // 返回平均值
}

function arr_diag(matrix) {
    return matrix.map((row, index) => row[index]);
}

function arr_slice(array, rows, base= 0, remove_string=true) {
    // array is a 2D array, index is rows
    let data = [];
    if (rows.length > 0) {
        data = numeric.transpose(array).filter((row, idx) => {
            if (!rows.includes(idx - base)) { return false }
            if (remove_string) {
                for (let i=0;i<row.length;i++) {
                    if (typeof row[i] === 'string' || row[i] instanceof String) { return false }
                }
            }
            return true;
        });
    }
    if (data.length > 0) {
        return numeric.transpose(data);
    } else {
        return [[], [], [], [], [], [], [], [], [], [], [], []];
    }
}

function dict_update(dict, x = {}) {
    for (const [key, value] of Object.entries(x)) {
        if (value.constructor === Object) {
            dict_update(dict[key], value);
        } else {
            dict[key] = value
        }
    }
    return dict;
}


// error propagation
function errAdd(...s) {
    return Math.sqrt(s.reduce((acc, val) => acc + val ** 2, 0))
}
function errMul(a, sa, b, sb) {
    return Math.sqrt(b ** 2 * sa ** 2 + a ** 2 * sb ** 2)
}
function errDiv(a, sa, b, sb) {
    return Math.sqrt(1/b ** 2 * sa ** 2 + a ** 2 * sb ** 2 / b ** 4)
}


// regression

function linest(a0, a1, ...args) {
    // Construct matrix of x and y, calculate the transpose of x
    let x;
    if (args.length === 0) {
        x = numeric.transpose([[...Array(a1.length).fill(1)], a1]);
    } else {
        x = numeric.transpose([[...Array(a1.length).fill(1)], a1, ...args]);
    }
    if (x.length === 0) {
        return false  // cl的图经常会有xy为空数组的情况会报错
    }
    const m = x.length; // number of data
    // const y = a0.map(val => [val]);
    const n = x[0].length; // number of unknown x, constant is seen as x^0
    const y = numeric.transpose([a0]);
    let inv_xtx;
    try {
        inv_xtx = numeric.inv(numeric.dot(numeric.transpose(x), x));
    } catch (error) {
        throw new Error("The determinant of the given matrix must not be zero");
    }

    const beta = numeric.dot(inv_xtx, numeric.dot(numeric.transpose(x), y));
    // Calculate Y values based on the fitted formula
    const estimate_y = numeric.dot(x, beta);
    const resid = arr_pow(arr_sub(numeric.transpose(estimate_y)[0], a0), 2);
    const reg = arr_pow(estimate_y.map(value => value - arr_mean(numeric.transpose(estimate_y)[0])), 2);
    const ssresid = arr_sum(resid);
    const ssreg = arr_sum(reg);
    const sstotal = ssreg + ssresid;
    const df = m - n;
    const m_ssresid = ssresid / df;
    const se_beta = arr_pow(arr_multiply_by_number(arr_diag(inv_xtx), m_ssresid), 0.5);
    const betaArray = numeric.transpose(beta)[0];
    const rse_beta = arr_div(se_beta, betaArray);
    const r2 = sstotal !== 0 ? ssreg / sstotal : Infinity;

    function get_adjusted_y(...args) {
        const adjusted_x = [[...Array(args[0].length).fill(1)], ...args];
        return adjusted_x[0].map((_, j) => arr_sum(adjusted_x.map((row, i) => row[j] * betaArray[i])));
    }

    return [betaArray[0], se_beta[0], rse_beta[0] * 100, r2, m_ssresid, betaArray, se_beta, get_adjusted_y, m_ssresid];
}


function york2(x, sx, y, sy, ri, f = 1, convergence = 0.001, iteration = 100) {
    const n = x.length;

    if (n < 3) {
        return false;
    }

    let X = [], sX = [], Y = [], sY = [], R = [];
    for (let i = 0; i < n; i++) {
        if (isFinite(x[i]) && !isNaN(x[i]) && isFinite(sx[i]) && !isNaN(sx[i]) &&
            isFinite(y[i]) && !isNaN(y[i]) && isFinite(sy[i]) && !isNaN(sy[i]) &&
            isFinite(ri[i]) && !isNaN(ri[i])) {
            X.push(x[i]);
            sX.push(sx[i]);
            Y.push(y[i]);
            sY.push(sy[i]);
            R.push(ri[i]);
        }
    }

    const wX = sX.map(s => 1 / (s ** 2));
    const wY = sY.map(s => 1 / (s ** 2));

    const Z = (m, b) => {
        return wX.map((wx, i) => wx * wY[i] / (m ** 2 * wY[i] + wx - 2 * m * R[i] * (wx * wY[i]) ** 0.5));
    };

    const mX = (m, b) => {
        const weights = Z(m, b);
        return X.reduce((sum, val, i) => sum + val * weights[i], 0) / weights.reduce((sum, val) => sum + val, 0);
    };

    const mY = (m, b) => {
        const weights = Z(m, b);
        return Y.reduce((sum, val, i) => sum + val * weights[i], 0) / weights.reduce((sum, val) => sum + val, 0);
    };

    const S = (m, b) => {
        const weights = Z(m, b);
        return weights.reduce((sum, val, i) => sum + val * (Y[i] - m * X[i] - b) ** 2, 0);
    };

    let [temp_b, temp_seb, temp_m, temp_sem, last_m] = [0, 0, 0, 0, 1e10];
    const linestResult = linest(Y, X); // Assume you have a linest function
    if (!linestResult) return false;
    [temp_b, temp_seb, temp_m, temp_sem] = [linestResult[5][0], linestResult[6][0], linestResult[5][1], linestResult[6][1]];
    let b = mY(temp_m, temp_b) - temp_m * mX(temp_m, temp_b);
    let Di = 0, mswd = 1, k = 1;
    while (Math.abs(temp_m - last_m) >= Math.abs(temp_m * convergence / 100)) {
        last_m = temp_m;
        const U = X.map((val, i) => val - mX(temp_m, b));
        const V = Y.map((val, i) => val - mY(temp_m, b));
        const Up = Z(temp_m, b).map((val, i) => val ** 2 * V[i] * (U[i] / wY[i] + temp_m * V[i] / wX[i] - R[i] * (V[i] + temp_m * U[i]) / (wX[i] * wY[i]) ** 0.5));
        const Lo = Z(temp_m, b).map((val, i) => val ** 2 * U[i] * (U[i] / wY[i] + temp_m * V[i] / wX[i] - R[i] * (V[i] + temp_m * U[i]) / (wX[i] * wY[i]) ** 0.5));
        temp_m = Up.reduce((sum, val) => sum + val, 0) / Lo.reduce((sum, val) => sum + val, 0);
        b = mY(temp_m, b) - temp_m * mX(temp_m, b);
        const sumUUZ = U.map((val, i) => val ** 2 * Z(temp_m, b)[i]).reduce((sum, val) => sum + val, 0);
        const sumXXZ = X.map((val, i) => val ** 2 * Z(temp_m, b)[i]).reduce((sum, val) => sum + val, 0);
        temp_sem = 1 / sumUUZ ** 0.5;
        temp_seb = (sumXXZ / Z(temp_m, b).reduce((sum, val) => sum + val, 0)) ** 0.5 * temp_sem;
        mswd = S(temp_m, b) / (n - 2);
        k = mswd > 1 ? mswd ** 0.5 : 1;
        temp_sem *= k;
        temp_seb *= k;

        Di++;
        if (Di >= iteration) break;
    }

    const estimate_y = X.map((val, i) => b + temp_m * val);
    const resid = estimate_y.map((val, i) => (val - Y[i]) ** 2);
    const reg = estimate_y.map((val, i) => (val - estimate_y.reduce((sum, val) => sum + val, 0) / n) ** 2);
    const ssresid = resid.reduce((sum, val) => sum + val, 0);
    const ssreg = reg.reduce((sum, val) => sum + val, 0);
    const sstotal = ssreg + ssresid;
    const r2 = sstotal !== 0 ? ssreg / sstotal : Infinity;
    const chi_square = mswd * (n - 2);
    // const p_value = distributions.chi2.sf(chi_square, n - 2);
    const p_value = 1 - jStat.chisquare.cdf(chi_square, n - 2);
    const err_s = (m, b) => Z(m, b).map((Zi, i) => (1 / Zi) ** 0.5 / Math.abs(Y[i] - m * X[i] - b));
    const avg_err_s = arr_mean(err_s(temp_m, b)) * 100;

    return [b, temp_seb, temp_m, temp_sem, mswd, Math.abs(temp_m - last_m), Di, k, r2, chi_square, p_value, avg_err_s];
}


function wtd3DRegression(x, sx, y, sy, z, sz, r1, r2, r3, f = 1, convergence = 0.001, iteration = 100) {
    // change to 1 sigma
    if (Number.isInteger(f) && f > 1) {
        sx = sx.map(val => val / f);
        sy = sy.map(val => val / f);
        sz = sz.map(val => val / f);
    }

    const n = x.length;
    // const x_arr = Array.from(x);
    // const sx_arr = Array.from(sx);
    // const y_arr = Array.from(y);
    // const sy_arr = Array.from(sy);
    // const z_arr = Array.from(z);
    // const sz_arr = Array.from(sz);
    // const r1_arr = Array.from(r1);
    // const r2_arr = Array.from(r2);
    // const r3_arr = Array.from(r3);

    if (n <= 3) {
        return false;
    }

    let Di = 0;

    // Weights of S
    const W = (a, b) => {
        return x.map((value, i) => {
            return 1 / (
                a ** 2 * sx[i] ** 2 + b ** 2 * sy[i] ** 2 + sz[i] ** 2 + 2 * a * b * r1[i] * sx[i] * sy[i] -
                2 * a * r2[i] * sx[i] * sz[i] - 2 * b * r3[i] * sy[i] * sz[i]
            );
        })
    }

    // Weighted mean values of X, Y, and Z, respectively
    const mX = (a, b) => x.reduce((sum, val, i) => sum + W(a, b)[i] * val, 0) / arr_sum(W(a, b));
    const mY = (a, b) => y.reduce((sum, val, i) => sum + W(a, b)[i] * val, 0) / arr_sum(W(a, b));
    const mZ = (a, b) => z.reduce((sum, val, i) => sum + W(a, b)[i] * val, 0) / arr_sum(W(a, b));

    // Minimizing this equation
    const S = (a, b, c) => {
        return arr_sum(W(a, b).map((Wi, i) => Wi * (a * x[i] + b * y[i] + c - z[i]) ** 2))
    };

    // Calculate new c based on iterated a and b
    const new_c = (a, b) => mZ(a, b) - a * mX(a, b) - b * mY(a, b);

    // Initial values of a, b, and c from OLS
    let [c, sc, k2, k3, k4, [_1, a, b], [_2, sa, sb]] = linest(z, x, y).slice(0, 7);
    let last_a = 1e10, k = 1, mswd = 1000; // Error magnification factor

    while (Math.abs(a - last_a) >= Math.abs(a * convergence / 100)) {
        last_a = a;
        let U = x.map((val, i) => val - mX(a, b));
        let V = y.map((val, i) => val - mY(a, b));
        let G = z.map((val, i) => val - mZ(a, b));

        let P = W(a, b).map((val, i) => val * ((a * sx[i] ** 2 + b * r1[i] * sx[i] * sy[i] - r2[i] * sx[i] * sz[i]) * (G[i] - b * V[i]) + (a * b * r1[i] * sx[i] * sy[i] + b ** 2 * sy[i] ** 2 - a * r2[i] * sx[i] * sz[i] - 2 * b * r3[i] * sy[i] * sz[i] + sz[i] ** 2) * U[i]));
        let Q = W(a, b).map((val, i) => val * ((b * sy[i] ** 2 + a * r1[i] * sx[i] * sy[i] - r3[i] * sy[i] * sz[i]) * (G[i] - a * U[i]) + (a * b * r1[i] * sx[i] * sy[i] + a ** 2 * sx[i] ** 2 - b * r3[i] * sy[i] * sz[i] - 2 * a * r2[i] * sx[i] * sz[i] + sz[i] ** 2) * V[i]));

        let a_Up = arr_sum(arr_mul(W(a, b), P, G)) * arr_sum(arr_mul(W(a, b), Q, V)) - arr_sum(arr_mul(W(a, b), P, V)) * arr_sum(arr_mul(W(a, b), Q, G))
        let a_Lo = arr_sum(arr_mul(W(a, b), P, U)) * arr_sum(arr_mul(W(a, b), Q, V)) - arr_sum(arr_mul(W(a, b), P, V)) * arr_sum(arr_mul(W(a, b), Q, U))

        let new_a = a_Up / a_Lo;

        let b_Up = arr_sum(arr_mul(W(a, b), Q, G)) * arr_sum(arr_mul(W(a, b), P, U)) - arr_sum(arr_mul(W(a, b), P, G)) * arr_sum(arr_mul(W(a, b), Q, U))
        let b_Lo = arr_sum(arr_mul(W(a, b), P, U)) * arr_sum(arr_mul(W(a, b), Q, V)) - arr_sum(arr_mul(W(a, b), P, V)) * arr_sum(arr_mul(W(a, b), Q, U))

        let new_b = b_Up / b_Lo;

        let mU = arr_sum(arr_mul(W(a, b), U)) / arr_sum(W(a, b));
        let mV = arr_sum(arr_mul(W(a, b), V)) / arr_sum(W(a, b));
        let mP = arr_sum(arr_mul(W(a, b), P)) / arr_sum(W(a, b));
        let mQ = arr_sum(arr_mul(W(a, b), Q)) / arr_sum(W(a, b));

        let WPU = arr_sum(arr_mul(W(a, b), P, U));
        let WQU = arr_sum(arr_mul(W(a, b), Q, U));
        let WQV = arr_sum(arr_mul(W(a, b), Q, V));
        let WPV = arr_sum(arr_mul(W(a, b), P, V));
        let WQG = arr_sum(arr_mul(W(a, b), Q, G));
        let WPG = arr_sum(arr_mul(W(a, b), P, G));

        let D_PU = W(a, b).map((Wi, i) => Wi * (a * b * r1[i] * sx[i] * sy[i] + b ** 2 * sy[i] ** 2 - a * r2[i] * sx[i] * sz[i] - 2 * b * r3[i] * sy[i] * sz[i] + sz[i] ** 2));
        let D_QU = W(a, b).map((Wi, i) => -1 * a * Wi * (b * sy[i] ** 2 + a * r1[i] * sx[i] * sy[i] - r3[i] * sy[i] * sz[i]));
        let D_PV = W(a, b).map((Wi, i) => -1 * b * Wi * (a * sx[i] ** 2 + b * r1[i] * sx[i] * sy[i] - r2[i] * sx[i] * sz[i]));
        let D_QV = W(a, b).map((Wi, i) => Wi * (a * b * r1[i] * sx[i] * sy[i] + a ** 2 * sx[i] ** 2 - b * r3[i] * sy[i] * sz[i] - 2 * a * r2[i] * sx[i] * sz[i] + sz[i] ** 2));
        let D_PG = W(a, b).map((Wi, i) => Wi * (a * sx[i] ** 2 + b * r1[i] * sx[i] * sy[i] - r2[i] * sx[i] * sz[i]));
        let D_QG = W(a, b).map((Wi, i) => Wi * (b * sy[i] ** 2 + a * r1[i] * sx[i] * sy[i] - r3[i] * sy[i] * sz[i]));

        let D_UX = W(a, b).map((Wi, i) => 1 - Wi / arr_sum(W(a, b)));
        let D_VY = W(a, b).map((Wi, i) => 1 - Wi / arr_sum(W(a, b)));
        let D_GZ = W(a, b).map((Wi, i) => 1 - Wi / arr_sum(W(a, b)));
        let D_Wa = W(a, b).map((Wi, i) => -1 * Wi ** 2 * (2 * a * sx[i] ** 2 + 2 * b * r1[i] * sx[i] * sy[i] - 2 * r2[i] * sx[i] * sz[i]));
        let D_Wb = W(a, b).map((Wi, i) => -1 * Wi ** 2 * (2 * b * sy[i] ** 2 + 2 * a * r1[i] * sx[i] * sy[i] - 2 * r3[i] * sy[i] * sz[i]));

        let D_aX = W(a, b).map((Wi, i) => Wi * D_UX[i] * (a * (WPU * V[i] * D_QU[i] + WQV * (U[i] * D_PU[i] + P[i]) - WQU * V[i] * D_PU[i] - WPV * (Q[i] + U[i] * D_QU[i])) -
            (WPG * V[i] * D_QU[i] + WQV * G[i] * D_PU[i]) + (WQG * V[i] * D_PU[i] + WPV * G[i] * D_QU[i])));

        let D_aY = W(a, b).map((Wi, i) => Wi * D_VY[i] * (a * (WPU * (Q[i] + V[i] * D_QV[i]) + WQV * U[i] * D_PV[i] - WQU * (P[i] + V[i] * D_PV[i]) - WPV * U[i] * D_QV[i]) -
            (WPG * (Q[i] + V[i] * D_QV[i]) + WQV * G[i] * D_PV[i]) + (WQG * (P[i] + V[i] * D_PV[i]) + WPV * G[i] * D_QV[i])));

        let D_aZ = W(a, b).map((Wi, i) => Wi * D_GZ[i] * (a * (WPU * V[i] * D_QG[i] + WQV * U[i] * D_PG[i] - WQU * V[i] * D_PG[i] - WPV * U[i] * D_QG[i]) -
            (WPG * V[i] * D_QG[i] + WQV * (P[i] + G[i] * D_PG[i])) + (WQG * V[i] * D_PG[i] + WPV * (Q[i] + G[i] * D_QG[i]))));

        let D_WPU_a = U.map((val, i) => D_Wa[i] * P[i] * U[i]);
        let D_WQV_a = U.map((val, i) => D_Wa[i] * Q[i] * V[i]);
        let D_WQU_a = U.map((val, i) => D_Wa[i] * Q[i] * U[i]);
        let D_WPV_a = U.map((val, i) => D_Wa[i] * P[i] * V[i]);
        let D_WPG_a = U.map((val, i) => D_Wa[i] * P[i] * G[i]);
        let D_WQG_a = U.map((val, i) => D_Wa[i] * Q[i] * G[i]);

        let D_aa = a_Lo + a *
            (arr_sum(D_WPU_a) * WQV + arr_sum(D_WQV_a) * WPU - arr_sum(D_WQU_a) * WPV - arr_sum(D_WPV_a) * WQU) -
            (arr_sum(D_WPG_a) * WQV + arr_sum(D_WQV_a) * WPG - arr_sum(D_WQG_a) * WPV - arr_sum(D_WPV_a) * WQG);

        let D_bX = W(a, b).map((Wi, i) => Wi * D_UX[i] * (b * (WPU * V[i] * D_QU[i] + WQV * (P[i] + U[i] * D_PU[i]) - WQU * V[i] * D_PU[i] - WPV * (Q[i] + U[i] * D_QU[i])) -
            (WQG * (P[i] + U[i] * D_PU[i]) + WPU * G[i] * D_QU[i]) + (WPG * (Q[i] + U[i] * D_QU[i]) + WQU * G[i] * D_PU[i]))
        );

        let D_bY = W(a, b).map((Wi, i) => Wi * D_VY[i] * (b * (WPU * (Q[i] + V[i] * D_QV[i]) + WQV * U[i] * D_PV[i] - WQU * (P[i] + V[i] * D_PV[i]) - WPV * U[i] * D_QV[i]) -
            (WQG * (U[i] * D_PV[i]) + WPU * (G[i] * D_QV[i])) + (WPG * (U[i] * D_QV[i]) + WQU * (G[i] * D_PV[i])))
        );

        let D_bZ = W(a, b).map((Wi, i) => Wi * D_GZ[i] * (b * (WPU * V[i] * D_QG[i] + WQV * (U[i] * D_PG[i]) - WQU * V[i] * D_PG[i] - WPV * (U[i] * D_QG[i])) -
            (WQG * (U[i] * D_PG[i]) + WPU * (Q[i] + G[i] * D_QG[i])) + (WPG * (U[i] * D_QG[i]) + WQU * (P[i] + G[i] * D_PG[i])))
        );

        let D_WPU_b = U.map((val, i) => D_Wb[i] * P[i] * U[i]);
        let D_WQV_b = U.map((val, i) => D_Wb[i] * Q[i] * V[i]);
        let D_WQU_b = U.map((val, i) => D_Wb[i] * Q[i] * U[i]);
        let D_WPV_b = U.map((val, i) => D_Wb[i] * P[i] * V[i]);
        let D_WPG_b = U.map((val, i) => D_Wb[i] * P[i] * G[i]);
        let D_WQG_b = U.map((val, i) => D_Wb[i] * Q[i] * G[i]);

        let D_bb = b_Lo + b *
            (arr_sum(D_WPU_b) * WQV + arr_sum(D_WQV_b) * WPU - arr_sum(D_WQU_b) * WPV - arr_sum(D_WPV_b) * WQU) -
            (arr_sum(D_WQG_b) * WPU + arr_sum(D_WPU_b) * WQG - arr_sum(D_WPG_b) * WQU - arr_sum(D_WQU_b) * WPG);

        let Va = arr_sum(U.map((val, i) => {
            return D_aX[i] ** 2 * sx[i] ** 2 + D_aY[i] ** 2 * sy[i] ** 2 + D_aZ[i] ** 2 * sz[i] ** 2 + 2 * r1[i] * sx[i] * sy[i] * D_aX[i] * D_aY[i] + 2 * r2[i] * sx[i] * sz[i] * D_aX[i] * D_aZ[i] + 2 * r3[i] * sy[i] * sz[i] * D_aY[i] * D_aZ[i]
        }));

        let Vb = arr_sum(U.map((val, i) => {
            return D_bX[i] ** 2 * sx[i] ** 2 + D_bY[i] ** 2 * sy[i] ** 2 + D_bZ[i] ** 2 * sz[i] ** 2 + 2 * r1[i] * sx[i] * sy[i] * D_bX[i] * D_bY[i] + 2 * r2[i] * sx[i] * sz[i] * D_bX[i] * D_bZ[i] + 2 * r3[i] * sy[i] * sz[i] * D_bY[i] * D_bZ[i]
        }));

        let D_cX = W(a, b).map((Wi, i) => {
            return -1 * a * Wi / arr_sum(W(a, b)) - D_aX[i] * (2 * mP - 2 * mU + mX(a, b)) - D_bX[i] * (2 * mQ - 2 * mV + mY(a, b))
        });

        let D_cY = W(a, b).map((Wi, i) => {
            return -1 * b * Wi / arr_sum(W(a, b)) - D_aY[i] * (2 * mP - 2 * mU + mX(a, b)) - D_bY[i] * (2 * mQ - 2 * mV + mY(a, b))
        });

        let D_cZ = W(a, b).map((Wi, i) => {
            return Wi / arr_sum(W(a, b)) - D_aZ[i] * (2 * mP - 2 * mU) - D_bZ[i] * (2 * mQ - 2 * mV)
        });

        let Vc = arr_sum(D_cX.map((_, i) => {
            return D_cX[i] ** 2 * sx[i] ** 2 + D_cY[i] ** 2 * sy[i] ** 2 + D_cZ[i] ** 2 * sz[i] ** 2 + 2 * r1[i] * sx[i] * sy[i] * D_cX[i] * D_cY[i] + 2 * r2[i] * sx[i] * sz[i] * D_cX[i] * D_cZ[i] + 2 * r3[i] * sy[i] * sz[i] * D_cY[i] * D_cZ[i]
        }));

        sa = Math.sqrt(Va / D_aa);
        sb = Math.sqrt(Vb / D_bb);
        sc = Math.sqrt(Vc);

        mswd = S(a, b, c) / (n - 3);

        if (mswd > 1) {
            k = Math.sqrt(mswd);
        } else {
            k = 1
        }

        sa *= k
        sb *= k
        sc *= k

        a = new_a;
        b = new_b;
        c = new_c(new_a, new_b);

        Di++;
        if (Di >= iteration) break;

    }

    const estimate_z = x.map((xi, i) => c + a * xi + b * y[i]);
    const resid = estimate_z.map((val, i) => (val - z[i]) ** 2);
    const reg = estimate_z.map((val, i) => (val - arr_mean(estimate_z)) ** 2);
    const ssresid = arr_sum(resid);
    const ssreg = arr_sum(reg);
    const sstotal = ssreg + ssresid;
    const R = sstotal!==0 ? ssreg / sstotal : np.inf;
    const chi_square = mswd * (n - 3);
    const p_value = 1 - jStat.chisquare.cdf(chi_square, n - 3);

    const err_s = (a, b, c) => W(a, b).map((Wi, i) => Math.sqrt(1 / Wi) / Math.abs(a * x[i] + b * y[i] + c - z[i]));
    const avg_err_s = arr_mean(err_s(a, b, c)) * 100;

    return [c, sc, a, sa, b, sb, S(a, b, c), mswd, R, Math.abs(a - last_a), Di, k, chi_square, p_value, avg_err_s];

}


function calcAgeMin(F, sF, conf) {
    // Convert kwargs object to JavaScript variables
    const J = conf['J'];
    const sJ = conf['sJ'];
    const A = conf['A'];
    const sA = conf['sA'];
    const Ae = conf['Ae'];
    const sAe = conf['sAe'];
    const Ab = conf['Ab'];
    const sAb = conf['sAb'];
    const W = conf['W'];
    const sW = conf['sW'];
    const Y = conf['Y'];
    const sY = conf['sY'];
    const f = conf['f'];
    // const sf = kwargs['sf'];
    const sf = 0;
    const No = conf['No'];
    const sNo = conf['sNo'];
    const L = conf['L'];
    const sL = conf['sL'];
    const Le = conf['Le'];
    const sLe = conf['sLe'];
    const Lb = conf['Lb'];
    const sLb = conf['sLb'];

    // standard age in year, change to Ma
    const t = conf['t'] * 1000000;
    const st = conf['st'] * 1000000;


    // recalculation using Min et al.(2000) equation
    const V = f * No / ((Ab + Ae) * W * Y);
    const sV = Math.sqrt(((V / f * sf) ** 2 + (V / No * sNo) ** 2 + (V / (Ab + Ae)) ** 2 * (sAb ** 2 + sAe ** 2) + (V / W * sW) ** 2 + (V / Y * sY) ** 2));

    // back-calculating Ar40/Ar39 ration for the standard
    const stdR = (Math.exp(t * L) - 1) / J;
    const sStdR = Math.sqrt((stdR / J) ** 2 * sJ ** 2);
    // normalize the measured 40Ar/39Ar
    const R = F / stdR;
    const sR_1 = Math.sqrt((sF / stdR) ** 2 + (F * sStdR / stdR ** 2) ** 2);
    const sR_2 = Math.sqrt((sF / stdR) ** 2);

    const BB = 1;
    const KK = Math.exp(t / V) - 1;
    const XX = BB * KK * R + 1;
    const age = V * Math.log(XX);
    let e1 = (Math.log(XX) * V / f - V * BB * KK * R / (f * XX)) ** 2 * sf ** 2;
    let e2 = (Math.log(XX) * V / No) ** 2 * sNo ** 2;
    let e3 = (-1 * Math.log(XX) * V / A + BB * KK * R / (A * XX)) ** 2 * sAb ** 2;
    let e4 = (-1 * Math.log(XX) * V / A - Ab * KK * R / (Ae ** 2 * XX)) ** 2 * sAe ** 2;
    let e5 = (-1 * Math.log(XX) * V / W - V * BB * KK * R / (W * XX)) ** 2 * sW ** 2;
    let e6 = (Math.log(XX) * V / Y) ** 2 * sY ** 2;
    let e7 = (V * BB * KK / XX) ** 2 * sR_1 ** 2;
    let e8 = 0;
    let e9 = 0;

    let useStandardAge = true;
    if (useStandardAge) {
        e1 = 0;
        e9 = 0;
    }

    // change to Ma
    const s1 = Math.sqrt((V * KK * R / (R * XX)) ** 2 * sR_2 ** 2);
    const s2 = Math.sqrt((V * KK * R / (R * XX)) ** 2 * sR_1 ** 2);
    const s3 = Math.sqrt(e1 + e2 + e3 + e4 + e5 + e6 + e7 + e8 + e9);
    return [age / 1000000, s1 / 1000000, s2 / 1000000, s3 / 1000000];
}


function calcAgeGeneral(F, sF, J, sJ, L, sL) {
    // Convert arguments to JavaScript arrays
    // F = Array.from(F);
    // sF = Array.from(sF);
    // J = Array.from(J);
    // sJ = Array.from(sJ);
    // L = Array.from(L);
    // sL = Array.from(sL);

    // Calculate age
    const age = Math.log(1 + J * F) / L;

    // Calculate variances
    const v1 = sF ** 2 * (J / (L * (1 + J * F))) ** 2;
    const v2 = sJ ** 2 * (F / (L * (1 + J * F))) ** 2;
    const v3 = sL ** 2 * (Math.log(1 + J * F) / (L ** 2)) ** 2;

    // Calculate errors
    const s1 = Math.sqrt(v1); // analytical error
    const s2 = Math.sqrt(v1 + v2); // internal error
    const s3 = Math.sqrt(v1 + v2 + v3); // full external error

    // Return results
    // Change to Ma
    return [age / 1000000, s1 / 1000000, s2 / 1000000, s3 / 1000000];
}



// for plotting

function getLinePoints(xscale, yscale, coeffs) {
    if (!Array.isArray(coeffs) || coeffs.length < 2) {
        throw new Error("Coeffs should be an array with length at least 2.");
    }

    const get_y = (x) => coeffs[0] + coeffs[1] * x;
    const get_x = (y) => (y - coeffs[0]) / coeffs[1] !== 0 ? (y - coeffs[0]) / coeffs[1] : null;
    const res = [];

    [[xscale[0], get_y(xscale[0])], [xscale[1], get_y(xscale[1])],
     [get_x(yscale[0]), yscale[0]], [get_x(yscale[1]), yscale[1]]].forEach((point) => {
        if (xscale[0] <= point[0] && point[0] <= xscale[1] && yscale[0] <= point[1] && point[1] <= yscale[1]) {
            res.push(point);
        }
    });

    return res;
}


function stepLinePoints(x, y) {
    // input:
    // x: array, y: array
    // output: points [x1, y1], [x1+x2, y1], [x1+x2, y2], ....
    const n = x.length;
    x = Array.from(
        {length: n + 1},
        (_, i) => i === 0 ? 0 : arr_sum(x.slice(0, i))
    );
    return Array.from(
        {length: n * 2},
        (_, i) => i % 2 === 0?[x[i/2], y[i/2]]:[x[(i+1)/2], y[(i-1)/2]]
    );
}


function ageSpectraPoints(ar39, age, sage, rows=null) {

    const age_1 = age.map((v, i) => i%2===0?v - sage[i]:v + sage[i]);
    const age_2 = age.map((v, i) => i%2===0?v + sage[i]:v - sage[i]);

    const step_points_1 = stepLinePoints(ar39, age_1);
    const step_points_2 = stepLinePoints(ar39, age_2);

    rows = rows ? rows : ar39.map((_, i) => i);
    const base = 0;
    const step_points = step_points_1.map((v, i) => [...v, step_points_2[i][1]]).filter((value, index) => {
        const row = Math.trunc(index / 2);
        return row >= Math.min(...rows) && row <= Math.max(...rows);
    })

    step_points.splice(0, 0,
        [step_points[0][0], step_points[0][2], step_points[0][1]]);
    step_points.push([step_points[step_points.length - 1][0],
        step_points[step_points.length - 1][2], step_points[step_points.length - 1][1]]);

    return step_points
}


function calcAr40r_39k(r, sr, ar36a, sar36a, ar39k, sar39k, ar40, sar40, ar40k, sar40k) {
    const ar40a = ar36a * r;
    const ar40r = ar40 - ar40k - ar40a
    return [
        ar40r / ar39k,
        errDiv(ar40r, errAdd(sar40, sar40k, errMul(ar36a, sar36a, r, sr)), ar39k, sar39k)
    ]

}

function weightedMeanValue(array_values, array_errors, adjust_error = true) {
    const weights = array_errors.map(v => 1 / v ** 2);
    const total_weight = arr_sum(weights);
    const df = array_values.length - 1;
    const k2 = array_values.length;
    const k0 = arr_sum(array_values.map((v, i) => v * weights[i] / total_weight)); // mean
    const k4 = arr_sum(array_values.map((v, i) => (v - k0) ** 2 * weights[i])); // chi_square
    const k3 = k4 / df; // MSWD mentioned in Min et al., 2000
    const k1 = adjust_error ? Math.sqrt(k3 / total_weight) : Math.sqrt(1 / total_weight);  // error
    const k5 = 1 - jStat.chisquare.cdf(k4, df);  // p value
    return [k0, k1, k2, k3, k4, k5]
}